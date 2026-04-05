# devops-for-the-horde

<div align="center">

<img src="https://raw.githubusercontent.com/shahzebqazi/devops-for-the-horde/main/docs/assets/logo-horde.png" alt="devops-for-the-horde logo" width="112" />

<br/><br/>

<img src="https://raw.githubusercontent.com/shahzebqazi/devops-for-the-horde/main/docs/assets/hero-horde-peons.jpg" alt="Hero art: stylized orc peon workers at glowing terminals in a crowded coding hall — original AI art for this project." width="780" />

<sub>Same artwork as the <a href="https://sqazi.sh/devops-for-the-horde/">live site</a> hero — theme only, not Blizzard IP.</sub>

<br/><br/>

<p align="center">
  <a href="https://github.com/shahzebqazi/devops-for-the-horde/actions/workflows/ci.yml"><img src="https://github.com/shahzebqazi/devops-for-the-horde/actions/workflows/ci.yml/badge.svg" alt="CI status" /></a>
  &nbsp;
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-2dd48a?style=flat-square" alt="MIT License" /></a>
  &nbsp;
  <a href="https://sqazi.sh/devops-for-the-horde/"><img src="https://img.shields.io/badge/site-sqazi.sh-1f6f4a?style=flat-square" alt="GitHub Pages site" /></a>
  &nbsp;
  <a href="flake.nix"><img src="https://img.shields.io/badge/flake-nix-5277C3?logo=nixos&logoColor=white&style=flat-square" alt="Nix flake" /></a>
</p>

**Personal Mac bootstrap hub** — one manifest, a small site, and room for Nix + agents to stay in sync.

[Live site](https://sqazi.sh/devops-for-the-horde/) · [Issues](https://github.com/shahzebqazi/devops-for-the-horde/issues) · [Email](mailto:willy@iconoclastaud.io)

<br/>

</div>

---

> Take a Mac from **fresh install** to **actually productive** without losing the thread.  
> Big direction change? Open an [**issue**](https://github.com/shahzebqazi/devops-for-the-horde/issues) first.

<br/>

## Contents

- [What this is for](#what-this-is-for)
- [How it fits together](#how-it-fits-together)
- [Mac → NixOS bootstrap and Nix umbrella](#mac-nixos)
- [Site (GitHub Pages)](#site-github-pages)
- [Contribute](#contribute)
- [License](#license)

---

## What this is for

- **Bootstrap a Mac quickly** — opinionated paths from clean install → productive (tooling, defaults, checks you can repeat).
- **Grow over time** — domains like computing, audio, coding, 3D, AI are yours to extend in [`config/master.yaml`](config/master.yaml).
- **Solo-first, fork-friendly** — optimize for your machine; borrow ideas if something helps.

---

## How it fits together

| Piece | Role |
| :--- | :--- |
| **[`config/master.yaml`](config/master.yaml)** | What belongs in this hub and which external repos to list. |
| **Linked repos** | Each repo owns its own automation; this one links and summarizes. |
| **Cursor + agents** | [`AGENTS.md`](AGENTS.md) and [`.cursor/rules`](.cursor/rules) keep README and site lists honest when manifests change. |

---

<h2 id="mac-nixos">Mac → NixOS bootstrap and Nix umbrella</h2>

| Topic | Where |
| :--- | :--- |
| **Inventory + playbook** | [`agent/mac-nixos-bootstrap/README.md`](agent/mac-nixos-bootstrap/README.md) — `collect-mac-state`, JSON schema, `make check`. |
| **Flakes** | Run `nix flake lock` once, **commit [`flake.lock`](flake.lock)**, then `nix develop` and `nix run .#` (**`horde-install-all`** clones linked repos under **`SATELLITE_ROOT`** — defaults use XDG; see [`nix/README.md`](nix/README.md)). |
| **Non-flake** | `nix-shell` via [`shell.nix`](shell.nix). |

---

## Site (GitHub Pages)

| | |
| :--- | :--- |
| **Canonical URL** | **[sqazi.sh/devops-for-the-horde](https://sqazi.sh/devops-for-the-horde/)** (`*.github.io` redirects here). |
| **Manifest on Pages** | The repo list loads from **`docs/config/master.yaml`** (a copy of the root file). After edits, run **`./scripts/sync-manifest.sh`** and commit so the live site matches. |
| **Assets** | Hero and logo live under `docs/assets/` (original AI art; theme only — not Blizzard IP). |

---

## Contribute

- **Ideas & discussion** — [Issues](https://github.com/shahzebqazi/devops-for-the-horde/issues); enable **Discussions** under repo **Settings → General** if you want threads.
- **Pull requests** — small PRs welcome; for large changes, open an issue first so plans do not collide.

---

## License

MIT — see **[LICENSE](LICENSE)**.

---

<div align="center">

<sub>Thanks for reading.</sub>

</div>
