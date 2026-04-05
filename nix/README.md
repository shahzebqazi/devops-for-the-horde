# Nix layout (hub)

This repo’s **flake** (`../flake.nix`) pins **nixpkgs** and exposes:

- **`nix develop`** — Python + `jsonschema` + `make` + `jq` (matches `shell.nix`).
- **`nix run .#`** — runs **`horde-install-all`**, which reads **`satellite-manifest.json`** at the repo root and, for each entry, clones into **`SATELLITE_ROOT`** (see below) and runs that repo’s **`nix/install.sh`**.

## Composable config (direction)

The long-term shape is an **independent Nix setup** assembled from **small modules** (e.g. per-host, per-role, or per-domain imports) rather than one giant `configuration.nix`. Work in this repo is aligned with that: the flake is the **umbrella**; linked repos remain **separate** checkouts with their own install scripts until you fold them into a single flake-driven system if you choose.

Nothing here assumes a **`~/Code`** path. Defaults use **XDG** state:

- **`SATELLITE_ROOT`** — where linked repos are cloned (default: `$XDG_STATE_HOME/devops-for-the-horde/linked-repos`, falling back to `~/.local/state/...` if `XDG_STATE_HOME` is unset).

Override explicitly when you want a different layout:

```bash
export SATELLITE_ROOT="$HOME/your/path"
nix run .#
```

## Lockfile

After changing `flake.nix` inputs, run **`nix flake lock`** and commit **`flake.lock`** so CI and others get the same **nixpkgs** revision.
