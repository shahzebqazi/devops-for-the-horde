# Agents (Cursor & friends)

## Purpose

This repo is the **central** **devops-for-the-horde** project: **master config** in `config/master.yaml`, **GitHub Pages** under `docs/`, and coordination docs.

When the user **adds, removes, or renames** satellite repositories—or changes **domains** in `master.yaml`—update:

1. **`README.md`** — Horde ops table, links, and domain summary if needed.
2. **`docs/index.html`** — “Satellite repos” / domains section if present (keep tone: solo-first, welcoming).
3. **No drive-by refactors** — touch only files needed to reflect manifest truth.

## Design cues

- **Landing page**: “glass” panels (blur, translucent layers, subtle borders), dark base, **Horde green** accents — inspired by Cursor-style glass UI, not a pixel copy of any product.
- **Warcraft flavor** is **thematic** (peons, Horde, humor). Do **not** embed Blizzard-owned art or rip game assets.

## Stock imagery

- Prefer **royalty-free** sources (e.g. Pexels, Unsplash) and **keep attribution** in `docs/index.html` when required by the license.

## Safety

- Do not commit secrets, tokens, or machine-specific paths that expose the user’s home layout beyond what they explicitly want public.
