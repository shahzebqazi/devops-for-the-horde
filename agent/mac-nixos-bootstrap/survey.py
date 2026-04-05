"""Pure helpers for *survey results* (no I/O).

These functions implement a small **functional core** for inventory semantics: the same
inputs always yield the same outputs (referential transparency), which keeps drift checks
and tests predictable while subprocess collection stays in `collect-mac-state.py` (I/O shell).

Ideas (informal mapping to FP literature):

- **Pure functions / equational reasoning** — John Hughes, *Why Functional Programming Matters*
  (modularity via small composable pieces). Here: canonicalize Homebrew lists, then hash.
- **Monoidal summary** — fold independent sets (leaves, casks, taps) into one digest that
  changes iff any component changes; same spirit as combining log-safe summaries.
- **Parse, don’t validate** (Alexis King / Neumann-style) — normalize data into a canonical
  form (sorted unique strings, fixed JSON shape) *before* comparing or hashing, instead of
  ad hoc string comparisons on raw `brew` output.

Use `inventory_digest` for `meta.inventoryDigest` so operators can diff two runs without
diffing entire JSON files.
"""

from __future__ import annotations

import hashlib
import json
from typing import Iterable


def inventory_digest(
    leaves: Iterable[str],
    casks: Iterable[str],
    taps: Iterable[str],
) -> str:
    """
    SHA-256 (hex) of a canonical JSON payload of sorted unique Homebrew *intent* lists.

    Excludes formulaeInstalled (transitive closure) on purpose: leaves + casks + taps
    match what playbook authors prioritize and what `INSTRUCTIONS.md` emphasizes.
    """
    payload = {
        "casksInstalled": sorted(set(c.strip() for c in casks if c.strip())),
        "leaves": sorted(set(x.strip() for x in leaves if x.strip())),
        "taps": sorted(set(t.strip() for t in taps if t.strip())),
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
