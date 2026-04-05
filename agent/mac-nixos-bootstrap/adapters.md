# Multi-tool adapters (future)

The workflow is **intentionally host-agnostic**: shell/Python collectors write artifacts; the **reasoning** lives in `INSTRUCTIONS.md` and can be pasted or loaded by any coding agent.

## Contract

1. **Inputs**
   - `machine-inventory-*.json` from `collect-mac-state.py`
   - Optional: repo-root `programs-and-dependencies.md` (richer `brew` dependency graph)
2. **Output**
   - `nixos-bootstrap-playbook.md` (from [`playbook-template.md`](playbook-template.md))

## Cursor (current)

- Enable rule: **Mac → NixOS bootstrap playbook** (see `.cursor/rules/mac-nixos-bootstrap.mdc`), or `@`-mention `INSTRUCTIONS.md` + latest inventory JSON.
- Keep artifacts out of git (`.gitignore`); attach files from `artifacts/` in the chat as needed.

## Codex / ChatGPT Codex CLI

- Run the collector locally; pass the JSON path as a file attachment or paste with `--redact`.
- Use the same `INSTRUCTIONS.md` system block as the “policy” for one-shot runs.

## Claude (Code / desktop)

- Add this directory as project knowledge or paste `INSTRUCTIONS.md` once per session.
- Prefer uploading JSON instead of pasting to avoid truncation on large `formulaeInstalled` lists; if too large, restrict to `leaves` + `casksInstalled` + `taps` + `meta.inventoryDigest` for the prompt.

## OpenCode / Pi / OpenClaw / other agent runners

- Map **project root** to this repo.
- Register a **task**: “Read `agent/mac-nixos-bootstrap/INSTRUCTIONS.md`, read latest inventory JSON, emit playbook from template.”
- If the runner supports **hooks**, optionally run `collect-mac-state.sh` before each planning session.

## Versioning

- Bump **`VERSION`** in `collect-mac-state.py` when the emitted JSON shape changes; update `schemas/inventory.schema.json` (required keys + descriptions) and `fixtures/minimal-inventory.json` when needed; run **`make check`** before pushing.
- Agents and humans should note **`meta.scriptVersion`** when comparing an old playbook to a new inventory—if versions differ, re-read `INSTRUCTIONS.md` for policy changes.
- The schema allows **extra properties** on `meta` / `system` / `homebrew` / root so CI does not break when new optional fields are added—keep **`required`** lists accurate when you add mandatory keys.

## CI

Validation runs in **GitHub Actions** on **macOS** (see [`.github/workflows/ci.yml`](../../.github/workflows/ci.yml)); locally, `make check` is the same commands on your machine.
