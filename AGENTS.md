# Agents (Cursor & friends)

## Purpose

This repo is the **central** **devops-for-the-horde** project: **master config** in `config/master.yaml`, **GitHub Pages** under `docs/`, and coordination docs. **Public site URL:** `https://sqazi.sh/devops-for-the-horde/`.

When the user **adds, removes, or renames** satellite repositories—or changes **domains** in `master.yaml`—update:

1. **`config/master.yaml`** — source of truth for `repositories` and `domains`.
2. **`./scripts/sync-manifest.sh`** — copies `config/master.yaml` → `docs/config/master.yaml` so the **live site** can fetch the manifest (same-origin). Run after every manifest edit, then commit **both** paths (or let CI do it if added later).
3. **`README.md`** — satellite bullets / links for readers on GitHub.
4. **`docs/index.html`** — only structural edits; the **Repos** `<ul id="repo-list">` is **filled by** `docs/js/satellites.js` from `docs/config/master.yaml` (do not hand-maintain duplicate repo rows unless fixing noscript fallback). Site/Pages notes and minicon previews live in **`docs/dev/index.html`** (dev-only; not linked from the main page).
5. **No drive-by refactors** — touch only files needed to reflect manifest truth.

## Mac → NixOS bootstrap playbook (in this repo)

The former **main-release** tooling now lives here:

- **Collector + schema + CI:** [`agent/mac-nixos-bootstrap/`](agent/mac-nixos-bootstrap/) — run `./agent/mac-nixos-bootstrap/collect-mac-state.sh` on macOS; validate with **`make check`** (see [`.github/workflows/ci.yml`](.github/workflows/ci.yml)).
- **Agent policy:** [`agent/mac-nixos-bootstrap/INSTRUCTIONS.md`](agent/mac-nixos-bootstrap/INSTRUCTIONS.md) — generate **`nixos-bootstrap-playbook.md`** at repo root or under **`docs/`**.
- **Cursor rule:** [`.cursor/rules/mac-nixos-bootstrap.mdc`](.cursor/rules/mac-nixos-bootstrap.mdc).
- **Nix umbrella:** [`flake.nix`](flake.nix), [`shell.nix`](shell.nix), [`satellite-manifest.json`](satellite-manifest.json), [`nix/install-all.sh`](nix/install-all.sh) — `nix develop`, `nix run .#` (default app runs **`horde-install-all`**).

Do not re-register this hub as a **satellite** in `satellite-manifest.json` (no self-clone).

## Agent tone (peon cadence, subtle)

*Warcraft III* peon voice lines are **flavor**, not spam. Use them as **internal rhythm** for agent behavior (see [Peon quotes on wiki.gg](https://warcraft.wiki.gg/wiki/Quotes_of_Warcraft_III/Orc_Horde#Peon)):

| Peon vibe | Agent habit |
|-----------|-------------|
| *“Something need doing?”* / *“What you want?”* | Before a non-trivial edit, confirm it matches `master.yaml` and the user’s last stated intent. |
| *“Work work.”* | Manifest sync is repetitive by design—ship small, consistent README + site updates. |
| *“I can do that.”* / *“Be happy to.”* / *“Okey dokey.”* | Scoped, requested changes only; no scope creep. |
| *“Work complete.”* | Stop when `master.yaml`, `docs/config/master.yaml`, README, and any touched site copy are aligned. |
| *“Me busy. Leave me alone!”* | Skip unrelated files, drive-bys, and “while I’m here” refactors. |

## Design cues

- **Landing page**: “glass” panels (blur, translucent layers, subtle borders), dark base, **Horde green** accents — inspired by Cursor-style glass UI, not a pixel copy of any product. **Hero art** should stay **visible**; overlays stay light; a **gradient bridge** blends into `--bg` before `main`.
- **Warcraft flavor** is **thematic** (peons, Horde, humor). Do **not** embed Blizzard-owned art or rip game assets.

## Site imagery

- **Hero + favicon** live under `docs/assets/` (AI-generated originals for this project). If you swap in stock photos instead, **keep attribution** in `docs/index.html` when the license requires it.

## Safety

- Do not commit secrets, tokens, or machine-specific paths that expose the user’s home layout beyond what they explicitly want public.
