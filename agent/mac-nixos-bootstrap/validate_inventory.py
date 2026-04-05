#!/usr/bin/env python3
"""Validate machine-inventory JSON against schemas/inventory.schema.json."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    from jsonschema import Draft202012Validator
except ImportError as e:
    print(
        "validate_inventory: install dev deps: pip install -r requirements-dev.txt",
        file=sys.stderr,
    )
    raise SystemExit(1) from e

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_SCHEMA = SCRIPT_DIR / "schemas" / "inventory.schema.json"
DEFAULT_FIXTURE = SCRIPT_DIR / "fixtures" / "minimal-inventory.json"


def load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def load_schema(path: Path) -> tuple[object | None, int]:
    """Load schema JSON. Returns (schema, 0) on success, (None, 1) on missing/unreadable/invalid file."""
    if not path.is_file():
        print(f"validate_inventory: schema not found or not a file: {path}", file=sys.stderr)
        return None, 1
    try:
        return load_json(path), 0
    except json.JSONDecodeError as e:
        print(f"validate_inventory: invalid JSON in schema {path}: {e}", file=sys.stderr)
        return None, 1
    except OSError as e:
        print(f"validate_inventory: cannot read schema {path}: {e}", file=sys.stderr)
        return None, 1


def validate(instance: object, schema: object, label: str) -> None:
    v = Draft202012Validator(schema)
    errors = sorted(v.iter_errors(instance), key=lambda e: e.path)
    if errors:
        lines = [f"{label}: schema validation failed:"]
        for err in errors:
            loc = "/".join(str(p) for p in err.path) if err.path else "(root)"
            lines.append(f"  - at {loc}: {err.message}")
        raise ValueError("\n".join(lines))


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--schema",
        type=Path,
        default=DEFAULT_SCHEMA,
        help="Path to inventory.schema.json",
    )
    p.add_argument(
        "--json",
        dest="json_path",
        type=Path,
        metavar="PATH",
        help="Inventory JSON to validate (default: validate fixture only)",
    )
    p.add_argument(
        "--fixture",
        action="store_true",
        help="Validate bundled minimal fixture (default when --json omitted)",
    )
    args = p.parse_args()

    schema, schema_err = load_schema(args.schema)
    if schema_err:
        return 1

    targets: list[tuple[str, Path]] = []
    if args.json_path:
        targets.append((str(args.json_path), args.json_path))
    if args.fixture:
        targets.append(("fixture", DEFAULT_FIXTURE))
    elif not args.json_path:
        targets.append(("fixture", DEFAULT_FIXTURE))

    # De-duplicate while preserving order
    seen: set[Path] = set()
    unique: list[tuple[str, Path]] = []
    for label, path in targets:
        rp = path.resolve()
        if rp in seen:
            continue
        seen.add(rp)
        unique.append((label, path))

    for label, path in unique:
        if not path.is_file():
            print(f"validate_inventory: not a file: {path}", file=sys.stderr)
            return 1
        try:
            instance = load_json(path)
        except json.JSONDecodeError as e:
            print(f"validate_inventory: invalid JSON in inventory {path}: {e}", file=sys.stderr)
            return 1
        except OSError as e:
            print(f"validate_inventory: cannot read inventory {path}: {e}", file=sys.stderr)
            return 1
        validate(instance, schema, label=f"{label} ({path.name})")
        print(f"OK: {label} — {path}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ValueError as e:
        print(str(e), file=sys.stderr)
        raise SystemExit(1)
