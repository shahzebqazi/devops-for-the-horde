#!/usr/bin/env python3
"""Snapshot macOS + Homebrew state into JSON (+ optional Markdown) for NixOS bootstrap planning."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from shutil import which
from typing import TextIO

from survey import inventory_digest

VERSION = "1.3.0"
SCRIPT_DIR = Path(__file__).resolve().parent

# Prevent hung subprocesses if brew or system tools block (local DoS / stuck terminal).
SUBPROCESS_TIMEOUT_SEC = 300
SHORT_TIMEOUT_SEC = 60
BREWFILE_MAX_BYTES = 512 * 1024

# When --redact: keep only these hardware keys (model class / capacity / chip family).
# All other profiler fields are dropped — not a legal/compliance guarantee; see --help.
SAFE_HARDWARE_KEYS = frozenset(
    {
        "chip_type",
        "machine_model",
        "machine_name",
        "model_number",
        "physical_memory",
        "number_processors",
        "cpu_type",
        "activation_lock_status",
    }
)


class _DebugState:
    """Set from main() when --debug or COLLECT_MAC_STATE_DEBUG is on."""

    on: bool = False
    run_dir: Path | None = None
    log_fp: TextIO | None = None


def dbg(msg: str) -> None:
    """Developer-oriented trace; never writes to stdout (keeps --print-json-path usable)."""
    line = f"collect-mac-state[debug]: {msg}"
    if _DebugState.on:
        print(line, file=sys.stderr)
    if _DebugState.log_fp:
        _DebugState.log_fp.write(line + "\n")
        _DebugState.log_fp.flush()


def open_debug_session(run_stamp: str) -> bool:
    """
    Create agent/mac-nixos-bootstrap/debug/run-<stamp>/ (gitignored) and open debug.log.
    Returns False if the directory or log file cannot be created.
    """
    dr = SCRIPT_DIR / "debug" / f"run-{run_stamp}"
    try:
        dr.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        print(f"collect-mac-state: cannot create debug directory {dr}: {e}", file=sys.stderr)
        return False
    log_path = dr / "debug.log"
    try:
        _DebugState.run_dir = dr
        _DebugState.log_fp = log_path.open("w", encoding="utf-8")
    except OSError as e:
        print(f"collect-mac-state: cannot write {log_path}: {e}", file=sys.stderr)
        _DebugState.run_dir = None
        _DebugState.log_fp = None
        try:
            dr.rmdir()
        except OSError:
            pass
        return False
    print(f"collect-mac-state: debug artifacts -> {dr.resolve()}", file=sys.stderr)
    return True


def close_debug_session() -> None:
    if _DebugState.log_fp:
        try:
            _DebugState.log_fp.close()
        except OSError:
            pass
        _DebugState.log_fp = None
    _DebugState.run_dir = None


def mirror_debug_outputs(
    run_dir: Path,
    *,
    json_path: Path,
    md_path: Path | None,
    out_dir: Path,
    notes_len: int,
) -> None:
    """Copy inventory outputs and write meta for local inspection under debug/run-*/."""
    try:
        shutil.copy2(json_path, run_dir / json_path.name)
        if md_path is not None and md_path.is_file():
            shutil.copy2(md_path, run_dir / md_path.name)
        meta = {
            "scriptVersion": VERSION,
            "argv": sys.argv,
            "cwd": str(Path.cwd()),
            "outputArtifactDir": str(out_dir.resolve()),
            "inventoryJson": json_path.name,
            "markdownCompanion": md_path.name if md_path and md_path.is_file() else None,
            "notesCount": notes_len,
        }
        (run_dir / "meta.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
        (run_dir / "README.txt").write_text(
            "Debug session (gitignored). Contents:\n"
            "  debug.log     — tee of all collect-mac-state[debug]: lines\n"
            "  meta.json     — argv, cwd, output paths\n"
            f"  {json_path.name} — copy of inventory JSON written to outputArtifactDir\n"
            + (
                f"  {md_path.name} — copy of Markdown companion\n"
                if md_path and md_path.is_file()
                else "  (no .md — run without --no-md to capture)\n"
            ),
            encoding="utf-8",
        )
    except OSError as e:
        dbg(f"warning: could not write debug mirror files: {e}")


def debug_env_enabled() -> bool:
    v = os.environ.get("COLLECT_MAC_STATE_DEBUG", "").strip().lower()
    return v in ("1", "true", "yes", "on")


def have_cmd(name: str) -> bool:
    return which(name) is not None


def _stderr_snippet(stderr: str | None, limit: int = 400) -> str:
    if not stderr:
        return ""
    s = stderr.strip().replace("\n", " ")
    if len(s) > limit:
        return s[:limit] + "…"
    return s


def run_text(
    cmd: list[str],
    *,
    notes: list[str],
    label: str,
    timeout: float = SUBPROCESS_TIMEOUT_SEC,
) -> str:
    """Run a command; on failure append to *notes* (with stderr snippet) instead of silent empty."""
    dbg(f"exec {label}: cmd={cmd!r} timeout={timeout}s")
    t0 = time.perf_counter()
    try:
        p = subprocess.run(
            cmd,
            text=True,
            capture_output=True,
            timeout=timeout,
        )
    except FileNotFoundError as e:
        elapsed = time.perf_counter() - t0
        dbg(f"fail {label}: FileNotFoundError after {elapsed:.3f}s — {e}")
        notes.append(f"{label}: command not found ({e})")
        return ""
    except subprocess.TimeoutExpired as e:
        elapsed = time.perf_counter() - t0
        dbg(f"fail {label}: TimeoutExpired after {elapsed:.3f}s (limit {timeout}s)")
        notes.append(f"{label}: timed out after {timeout}s")
        return ""
    except OSError as e:
        elapsed = time.perf_counter() - t0
        dbg(f"fail {label}: OSError after {elapsed:.3f}s — {e}")
        notes.append(f"{label}: {e}")
        return ""

    elapsed = time.perf_counter() - t0
    out = (p.stdout or "").strip()
    if p.returncode != 0:
        err = _stderr_snippet(p.stderr)
        dbg(f"fail {label}: rc={p.returncode} in {elapsed:.3f}s stderr={err!r}")
        notes.append(
            f"{label}: exited {p.returncode}"
            + (f" ({err})" if err else "")
        )
        return ""
    dbg(f"ok {label}: rc=0 in {elapsed:.3f}s stdout_chars={len(out)}")
    if p.stderr and str(p.stderr).strip():
        dbg(f"stderr {label} (non-fatal): {_stderr_snippet(p.stderr, 800)!r}")
    return out


def run_json(
    cmd: list[str],
    *,
    notes: list[str],
    label: str,
    timeout: float = SHORT_TIMEOUT_SEC,
) -> object:
    raw = run_text(cmd, notes=notes, label=label, timeout=timeout)
    if not raw:
        return {}
    try:
        data = json.loads(raw)
        if isinstance(data, dict):
            dbg(f"json {label}: root object keys={list(data.keys())[:20]!r}{'…' if len(data) > 20 else ''}")
        else:
            dbg(f"json {label}: root type={type(data).__name__}")
        return data
    except json.JSONDecodeError as e:
        dbg(f"json {label}: JSONDecodeError — {e}")
        notes.append(f"{label}: invalid JSON from subprocess ({e})")
        return {}


def path_presence(home: Path) -> dict[str, bool]:
    candidates = [
        ".profile",
        ".bash_profile",
        ".bashrc",
        ".zprofile",
        ".zshrc",
        ".config/fish/config.fish",
        ".xonshrc",
        ".tmux.conf",
        ".config/git/config",
        ".gitconfig",
        ".config/nvim",
        ".vimrc",
        ".ssh/config",
        "Brewfile",
    ]
    out: dict[str, bool] = {}
    for c in candidates:
        p = home / c
        out[c] = p.is_file() or p.is_dir()
    return out


def sw_vers(notes: list[str]) -> dict[str, str]:
    if not have_cmd("sw_vers"):
        dbg("skip sw_vers: sw_vers not on PATH")
        notes.append("sw_vers not on PATH; system.sw_vers is empty.")
        return {}
    return {
        "productName": run_text(
            ["sw_vers", "-productName"],
            notes=notes,
            label="sw_vers -productName",
            timeout=SHORT_TIMEOUT_SEC,
        ),
        "productVersion": run_text(
            ["sw_vers", "-productVersion"],
            notes=notes,
            label="sw_vers -productVersion",
            timeout=SHORT_TIMEOUT_SEC,
        ),
        "buildVersion": run_text(
            ["sw_vers", "-buildVersion"],
            notes=notes,
            label="sw_vers -buildVersion",
            timeout=SHORT_TIMEOUT_SEC,
        ),
    }


def hardware_json(notes: list[str]) -> dict:
    if not have_cmd("system_profiler"):
        dbg("skip hardware: system_profiler not on PATH")
        notes.append(
            "system_profiler not available (not macOS or not on PATH); system.hardware is empty."
        )
        return {}
    data = run_json(
        ["system_profiler", "SPHardwareDataType", "-json"],
        notes=notes,
        label="system_profiler SPHardwareDataType",
        timeout=SHORT_TIMEOUT_SEC,
    )
    if not isinstance(data, dict):
        notes.append(
            "system_profiler returned unexpected JSON root (expected object); system.hardware is empty."
        )
        return {}
    rows = data.get("SPHardwareDataType")
    if rows is None:
        notes.append(
            "system_profiler JSON missing SPHardwareDataType key (format may have changed); system.hardware is empty."
        )
        return {}
    if not isinstance(rows, list) or not rows:
        notes.append("system_profiler SPHardwareDataType is empty; system.hardware is empty.")
        return {}
    first = rows[0]
    if not isinstance(first, dict):
        notes.append("system_profiler SPHardwareDataType[0] is not an object; system.hardware is empty.")
        return {}
    dbg(f"hardware: SPHardwareDataType[0] keys={list(first.keys())!r}")
    return first


def brew_exe() -> str | None:
    """Resolve `brew` on PATH, or None if not installed / not executable."""
    path = which("brew")
    if not path:
        dbg("brew: which('brew') -> None")
        return None
    try:
        if not os.access(path, os.X_OK):
            dbg(f"brew: not executable — {path!r}")
            return None
    except OSError as e:
        dbg(f"brew: os.access failed — {e}")
        return None
    dbg(f"brew: using {path!r}")
    return path


def brew_lines(
    brew_path: str | None,
    subargs: list[str],
    *,
    notes: list[str],
    label: str,
) -> list[str]:
    """Run `brew <subargs>` only when *brew_path* is set; never call brew otherwise."""
    if not brew_path:
        dbg(f"skip {label}: no brew path")
        return []
    cmd = [brew_path, *subargs]
    out = run_text(cmd, notes=notes, label=label)
    if not out:
        return []
    lines = sorted({line.strip() for line in out.splitlines() if line.strip()})
    dbg(f"{label}: {len(lines)} lines")
    return lines


def collect_homebrew(
    b: str | None,
    notes: list[str],
) -> tuple[str, str, list[str], list[str], list[str], list[str]]:
    """
    Gather Homebrew metadata and package lists. All brew subprocesses are gated on *b*.
    Returns: prefix, version, taps, formulae, casks, leaves.
    """
    if not b:
        dbg("collect_homebrew: skipped (no brew)")
        return "", "", [], [], [], []

    prefix = run_text([b, "--prefix"], notes=notes, label="brew --prefix")
    brew_version = ""
    ver_out = run_text([b, "--version"], notes=notes, label="brew --version")
    lines = ver_out.splitlines()
    brew_version = lines[0].strip() if lines else ""
    if not brew_version:
        notes.append("`brew` is on PATH but did not return a version string; lists may still be empty.")

    tap_out = run_text([b, "tap"], notes=notes, label="brew tap")
    taps = sorted({line.strip() for line in tap_out.splitlines() if line.strip()})

    formulae = brew_lines(b, ["list", "--formula"], notes=notes, label="brew list --formula")
    casks = brew_lines(b, ["list", "--cask"], notes=notes, label="brew list --cask")
    leaves = brew_lines(b, ["leaves"], notes=notes, label="brew leaves")
    return prefix, brew_version, taps, formulae, casks, leaves


def redact_hardware(hw: dict) -> dict:
    """
    For sharing: keep only coarse, non-identifying hardware fields.
    Does not satisfy strict compliance regimes by itself — review before publishing.
    """
    if not hw:
        return hw
    return {k: hw[k] for k in SAFE_HARDWARE_KEYS if k in hw}


def read_login_shell(home: Path, notes: list[str]) -> str:
    if not have_cmd("dscl"):
        dbg("skip loginShell: dscl not on PATH")
        notes.append("dscl not available; loginShell not queried.")
        return ""
    ds = run_text(
        ["dscl", ".", "-read", str(home), "UserShell"],
        notes=notes,
        label="dscl UserShell",
        timeout=SHORT_TIMEOUT_SEC,
    )
    if not ds.strip():
        notes.append(
            "dscl returned no stdout for UserShell; loginShell left empty (account path may be wrong)."
        )
        return ""
    for line in ds.splitlines():
        stripped = line.strip()
        if stripped.startswith("UserShell:"):
            shell = stripped.split(":", 1)[1].strip()
            dbg(f"loginShell: parsed {shell!r}")
            return shell
    notes.append("dscl output did not contain a UserShell line; loginShell left empty.")
    return ""


def read_brewfile_limited(path: Path, max_bytes: int) -> tuple[str | None, str | None]:
    """
    Read Brewfile with a size cap and tolerant decoding.
    Returns (content, error_note) where error_note is set on failure or truncation.
    """
    try:
        st = path.stat()
    except OSError as e:
        return None, f"Could not stat Brewfile: {e}"
    if st.st_size > max_bytes:
        return None, f"Brewfile exceeds max size ({max_bytes} bytes); skipped."
    try:
        data = path.read_bytes()
    except OSError as e:
        return None, f"Could not read Brewfile: {e}"
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        text = data.decode("utf-8", errors="replace")
        return text, "Brewfile contained invalid UTF-8; replaced undecodable bytes."
    return text, None


def inventory_stamp() -> str:
    """Wall-clock stamp with microseconds to avoid overwriting two runs in the same second."""
    return datetime.now().strftime("%Y%m%d-%H%M%S-%f")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "-o",
        "--output-dir",
        default=str(SCRIPT_DIR / "artifacts"),
        help="Output directory (default: agent/mac-nixos-bootstrap/artifacts)",
    )
    p.add_argument("--no-md", action="store_true", help="Skip Markdown companion file")
    p.add_argument(
        "--redact",
        action="store_true",
        help=(
            "Redact hostname and restrict hardware to coarse fields only (see SAFE_HARDWARE_KEYS in script). "
            "Not a legal/compliance guarantee."
        ),
    )
    p.add_argument(
        "--print-json-path",
        action="store_true",
        help="Print absolute path of written JSON to stdout (one line) for tooling; messages stay on stderr.",
    )
    p.add_argument(
        "--debug",
        "-d",
        action="store_true",
        help=(
            "Developer mode: stderr trace plus a gitignored directory "
            f"({SCRIPT_DIR.name}/debug/run-<stamp>/) with debug.log, meta.json, and copies of outputs."
        ),
    )
    p.add_argument(
        "--no-debug",
        action="store_true",
        help="Disable debug even if COLLECT_MAC_STATE_DEBUG is set in the environment.",
    )
    args = p.parse_args()

    if args.no_debug:
        _DebugState.on = False
    elif args.debug:
        _DebugState.on = True
    else:
        _DebugState.on = debug_env_enabled()

    run_stamp = inventory_stamp()

    if _DebugState.on:
        if not open_debug_session(run_stamp):
            return 1

    try:
        return _run_collect(args, run_stamp)
    finally:
        close_debug_session()


def _run_collect(args: argparse.Namespace, run_stamp: str) -> int:
    out_dir = Path(args.output_dir).expanduser().resolve()
    try:
        out_dir.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        print(f"collect-mac-state: cannot create output directory {out_dir}: {e}", file=sys.stderr)
        return 1

    home = Path.home()
    dbg(f"bootstrap version={VERSION} debug={_DebugState.on}")
    dbg(f"python={sys.executable!r} cwd={os.getcwd()!r}")
    dbg(f"out_dir={out_dir!s} HOME={home!s}")

    notes: list[str] = []

    b = brew_exe()
    if not b:
        msg = (
            "Homebrew not found (not on PATH or not executable); "
            "homebrew.* lists will be empty. System paths and optional Brewfile text are still collected."
        )
        notes.append(msg)
        print(f"collect-mac-state: {msg}", file=sys.stderr)

    brew_prefix, brew_version, taps, formulae, casks, leaves = collect_homebrew(b, notes)

    brewfile = None
    bf = home / "Brewfile"
    if bf.is_file():
        content, bf_note = read_brewfile_limited(bf, BREWFILE_MAX_BYTES)
        brewfile = content
        if bf_note:
            notes.append(bf_note)
        if not b and content is not None:
            notes.append("Brewfile present; captured for reference even though Homebrew is not installed.")

    login_shell = read_login_shell(home, notes)

    hw = hardware_json(notes)
    if args.redact:
        hw = redact_hardware(hw)
        notes.append(
            "Redacted: hostname replaced; hardware reduced to coarse fields only (--redact). "
            "Review before sharing."
        )

    hostname = run_text(
        ["hostname"],
        notes=notes,
        label="hostname",
        timeout=SHORT_TIMEOUT_SEC,
    ) or ""
    if args.redact:
        hostname = "<redacted>"

    digest = inventory_digest(leaves, casks, taps)

    data = {
        "meta": {
            "collectedAt": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            "hostname": hostname,
            "source": "collect-mac-state.py",
            "scriptVersion": VERSION,
            "inventoryDigest": digest,
        },
        "system": {
            "sw_vers": sw_vers(notes),
            "uname": run_text(["uname", "-a"], notes=notes, label="uname -a", timeout=SHORT_TIMEOUT_SEC),
            "arch": run_text(["uname", "-m"], notes=notes, label="uname -m", timeout=SHORT_TIMEOUT_SEC),
            "hardware": hw,
            "shell": os.environ.get("SHELL", ""),
            "loginShell": login_shell,
        },
        "paths": path_presence(home),
        "homebrew": {
            "prefix": brew_prefix,
            "version": brew_version,
            "taps": taps,
            "formulaeInstalled": formulae,
            "casksInstalled": casks,
            "leaves": leaves,
            "brewfile": brewfile,
        },
        "notes": notes,
    }

    json_path = out_dir / f"machine-inventory-{run_stamp}.json"
    try:
        json_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    except OSError as e:
        print(f"collect-mac-state: cannot write {json_path}: {e}", file=sys.stderr)
        return 1
    print(f"Wrote {json_path}", file=sys.stderr)
    dbg(f"summary notes={len(notes)} formulae={len(data['homebrew']['formulaeInstalled'])} casks={len(data['homebrew']['casksInstalled'])}")

    if args.print_json_path:
        print(json_path.resolve(), file=sys.stdout)

    # Mirror JSON as soon as it exists so a later Markdown write failure still leaves a full debug copy.
    if _DebugState.run_dir:
        mirror_debug_outputs(
            _DebugState.run_dir,
            json_path=json_path,
            md_path=None,
            out_dir=out_dir,
            notes_len=len(notes),
        )

    md_path: Path | None = None
    if not args.no_md:
        md_path = out_dir / f"machine-inventory-{run_stamp}.md"
        lines = [
            "# Machine inventory snapshot",
            "",
            f"Generated: **{run_stamp}** (see JSON `meta.collectedAt` for UTC).",
            f"**Intent digest** (`meta.inventoryDigest`): `{digest}`",
            "",
            "## System",
            "",
            f"- Hostname: `{data['meta']['hostname']}`",
            f"- Arch: `{data['system']['arch']}`",
            "",
            "```",
            data["system"]["uname"],
            "```",
            "",
            "## Homebrew",
            "",
        ]
        if data["homebrew"]["version"]:
            lines.extend(
                [
                    f"- {data['homebrew']['version']}",
                    f"- Prefix: `{data['homebrew']['prefix']}`",
                ]
            )
        else:
            lines.append("- (not available)")
        lines.extend(["", f"Full data: `{json_path.name}`", ""])
        try:
            md_path.write_text("\n".join(lines), encoding="utf-8")
        except OSError as e:
            print(f"collect-mac-state: cannot write {md_path}: {e}", file=sys.stderr)
            return 1
        print(f"Wrote {md_path}", file=sys.stderr)
        if _DebugState.run_dir:
            mirror_debug_outputs(
                _DebugState.run_dir,
                json_path=json_path,
                md_path=md_path,
                out_dir=out_dir,
                notes_len=len(notes),
            )

    if _DebugState.run_dir:
        dbg(f"debug mirror: {_DebugState.run_dir.resolve()}")

    dbg("done OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
