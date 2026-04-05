# devops-for-the-horde

> *“Work complete.”* — take a Mac from **zero to raid-ready** in minutes, not weekends.  
> *“Something need doing?”* — open an [issue](https://github.com/shahzebqazi/devops-for-the-horde/issues) before a big direction change.

**devops-for-the-horde** is the **central command post**: one **master config**, many **satellite repos** (apps, dotfiles, stacks), and **Cursor-first** workflows so you (and future agents) can evolve the base without losing the plot.

| You are here | Role |
|--------------|------|
| This repo | **Orc burrow**: master config, site, and coordination docs |
| Other repos | **Specialized units**: per-app automation, Nix/Homebrew slices, experiments |

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

---

## Site (GitHub Pages)

- **Landing page**: [sqazi.sh/devops-for-the-horde](https://sqazi.sh/devops-for-the-horde/) (canonical; `*.github.io` redirects here).
- **Hero & logo**: original AI-generated assets in `docs/assets/` (orc-peon coding horde theme). WC3 *flavor*, not Blizzard IP.

---

## Contribute

- **Ideas & discussion**: [Issues](https://github.com/shahzebqazi/devops-for-the-horde/issues) and **GitHub Discussions** (enable under repo Settings → General if not on yet).
- **Changes**: small PRs welcome; for large direction changes, open an issue first so we don’t collide builds.

---

## License

MIT — see [LICENSE](LICENSE).

---

*For the Warchief of your own rig. Lok’tar.*
