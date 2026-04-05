# Mac → NixOS bootstrap playbook agent

This folder defines a **file-based agent protocol**: collect machine state on macOS, then have an AI (Cursor today; other tools later) generate a **NixOS operations bootstrap playbook**—not a line-for-line port of Homebrew, but a phased plan to reproduce your *roles* (dev, media, CLI, GUI) on NixOS.

## Quick start

1. From the repo root:

   ```bash
   ./agent/mac-nixos-bootstrap/collect-mac-state.sh
   ```

   Or: `python3 agent/mac-nixos-bootstrap/collect-mac-state.py -o ./out`

2. Open the newest `machine-inventory-*.json` under `artifacts/` (gitignored) together with [`INSTRUCTIONS.md`](INSTRUCTIONS.md) in Cursor and ask for a playbook.

3. Save the result as `nixos-bootstrap-playbook.md` at the repo root (or `docs/`) and iterate.

**Privacy:** Inventory JSON can include hostname and hardware identifiers. Artifacts are gitignored by default. Use **`--redact`** to replace the hostname and keep only **coarse** hardware fields (see `SAFE_HARDWARE_KEYS` in `collect-mac-state.py`). That is **not** a legal/compliance guarantee—review before publishing. Brewfile content is capped (512 KiB) to avoid accidental huge reads.

**No Homebrew:** If `brew` is not on `PATH` or is not executable, the script still exits successfully: system info, dotfile path presence, and optional `~/Brewfile` text are collected; `homebrew.*` package lists stay empty and `notes` explain the situation (also printed to stderr).

**Subprocess failures:** Non-zero exits and stderr snippets are recorded in **`notes`** (stdout/stderr from the collector itself stays on stderr for “Wrote …” lines).

**Debug mode (developers):** Use **`--debug`** / **`-d`** or set **`COLLECT_MAC_STATE_DEBUG=1`** (also `true`, `yes`, `on`) to print **`collect-mac-state[debug]:`** lines to **stderr** and create a **gitignored** folder **`debug/run-<stamp>/`** next to this script: **`debug.log`** (same lines as stderr), **`meta.json`** (argv, cwd, output paths), **`README.txt`**, and **copies** of the inventory JSON / Markdown (same filenames as under `-o`). Use **`--no-debug`** to force off when the env var is set. Debug never writes trace lines to **stdout** (so **`--print-json-path`** stays machine-parseable).

## Files

| File | Role |
|------|------|
| `collect-mac-state.py` | Collects system + Homebrew + dotfile path presence |
| `survey.py` | Pure helpers (e.g. `inventory_digest` for `meta.inventoryDigest`) |
| `collect-mac-state.sh` | Wrapper calling the Python implementation |
| `schemas/inventory.schema.json` | JSON shape for tooling and validation |
| `playbook-template.md` | Skeleton for generated playbooks |
| `INSTRUCTIONS.md` | Full agent behavior (what to analyze, how to map to NixOS) |
| `adapters.md` | How to run the same workflow in Codex, Claude Code, OpenCode, etc. |

## Relationship to `programs-and-dependencies.md`

If the repo contains a manual Homebrew snapshot (for example `programs-and-dependencies.md` with `brew deps --installed`), the agent should use it as **supplementary** dependency graph detail when present.

## CI / local checks

From the repo root, **`make check`** compiles Python, validates the [bundled fixture](fixtures/minimal-inventory.json) against [`schemas/inventory.schema.json`](schemas/inventory.schema.json), then runs `collect-mac-state.py` to a temp directory and validates the emitted JSON. Requires [`requirements-dev.txt`](../../requirements-dev.txt) (installed automatically by Make). See the root [`README.md`](../../README.md).

**GitHub Actions:** The same target runs in CI via [`.github/workflows/ci.yml`](../../.github/workflows/ci.yml) on **hosted `macos-latest`** runners. That is separate from running `make check` on your own Mac.
