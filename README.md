# devops-for-the-horde

> *“Work complete.”* — take a Mac from **zero to raid-ready** in minutes, not weekends.  
> *“Something need doing?”* — open an [issue](https://github.com/shahzebqazi/devops-for-the-horde/issues) before a big direction change.

**devops-for-the-horde** is the **central command post**: one **master config**, many **satellite repos** (apps, dotfiles, stacks), and **Cursor-first** workflows so you (and future agents) can evolve the base without losing the plot.

| You are here | Role |
|--------------|------|
| This repo | **Orc burrow**: master config, site, and coordination docs |
| Other repos | **Specialized units**: per-app automation, Nix/Homebrew slices, experiments |

**Satellite repos** (see [`config/master.yaml`](config/master.yaml)) are listed on the site and in the manifest; the **Mac → NixOS bootstrap collector**, **flake umbrella**, and **`nix/install-all`** orchestration live **in this repository** ([`agent/mac-nixos-bootstrap/`](agent/mac-nixos-bootstrap/), [`flake.nix`](flake.nix), [`satellite-manifest.json`](satellite-manifest.json)).

**Contact:** [willy@iconoclastaud.io](mailto:willy@iconoclastaud.io)

---

## What this is for

- **Bootstrap a Mac fast**: opinionated paths from fresh install → productive (tooling, defaults, verification).
- **Personal domains** (expand as you add repos): general computing, game development, pro audio & music, coding, 3D, AI lab, and whatever the next expansion brings.
- **Solo-first, fork-friendly**: you optimize for *your* machine; others can steal ideas and open issues.

---

## Horde ops (how it fits together)

1. **`config/master.yaml`** — single source of truth for “what belongs in the horde” (repos, tiers, domains).
2. **Satellite repos** — own their app-specific automation; this repo links and summarizes.
3. **Cursor + agents** — use `AGENTS.md` and `.cursor/rules` so an agent can refresh README/site lists when you add or rename repos (*work work*—straight, repeatable sync; you stay in control; commits still go through you).

## Mac → NixOS bootstrap & Nix umbrella

- **Inventory + playbook workflow:** [`agent/mac-nixos-bootstrap/README.md`](agent/mac-nixos-bootstrap/README.md) — `collect-mac-state`, JSON schema, `make check`.
- **Flakes:** `nix flake lock` once, then `nix develop`, `nix run .#` (runs **`horde-install-all`** — clones satellites under `$SATELLITE_ROOT` and runs each `nix/install.sh`). **Non-flake:** `nix-shell` via [`shell.nix`](shell.nix).

---

## Site (GitHub Pages)

- **Landing page**: [sqazi.sh/devops-for-the-horde](https://sqazi.sh/devops-for-the-horde/) (canonical; `*.github.io` redirects here).
- **Hero & logo**: original AI-generated assets in `docs/assets/` (orc-peon coding horde theme). WC3 *flavor*, not Blizzard IP.
- **Satellite list** on the site loads from **`docs/config/master.yaml`** (a copy of `config/master.yaml`). After editing the root manifest, run **`./scripts/sync-manifest.sh`** and commit so Pages serves the updated file.

---

## Contribute

- **Ideas & discussion**: [Issues](https://github.com/shahzebqazi/devops-for-the-horde/issues) and **GitHub Discussions** (enable under repo Settings → General if not on yet).
- **Changes**: small PRs welcome; for large direction changes, open an issue first so we don’t collide builds.

---

## License

MIT — see [LICENSE](LICENSE).

---

*For the Warchief of your own rig. Lok’tar.*
