# NixOS operations bootstrap playbook

**Subject machine (source):** macOS inventory `machine-inventory-*.json` (and optional `programs-and-dependencies.md`)

**Target:** NixOS (state version: _fill after you pick a channel_)

**Owner / environment:** _personal workstation | work laptop | server_

---

## 1. Executive summary

- **Roles to reproduce:** _e.g. dev (Rust, Haskell, Python), CLI, terminal multiplexer, selected GUI apps_
- **Non-goals:** _what we are not automating in v1 (e.g. proprietary DAW, licensed IDE)_
- **Risk level:** _low | medium | high_ (disk layout changes, unfree packages, virtualization)
- **End state:** **Nix** on NixOS (nixpkgs / Home Manager as needed). Homebrew in the inventory is **input for mapping only**—on NixOS you **do not** recreate Homebrew; you replace brew-managed intent with Nix-native modules and packages.

---

## 2. Source inventory highlights

| Area | macOS signal | NixOS direction |
|------|----------------|-----------------|
| CPU / RAM | From `system.hardware` | HW-specific kernel params if needed |
| Shell / dotfiles | `paths`, login shell | `home-manager` or declarative `environment` |
| Top-level brew leaves | `homebrew.leaves` | Map to `nixpkgs` names / modules |
| Casks | `homebrew.casksInstalled` | GUI: `nixpkgs`, Flatpak, or manual with documented imperative steps |
| Taps | `homebrew.taps` | Custom packages or flakes if no upstream equivalent |
| Drift | `meta.inventoryDigest` | Compare across two collector runs (same digest ⇒ same leaves/casks/taps intent) |

---

## 2b. Channels **not** covered by this inventory

The JSON does **not** reliably enumerate:

- **Mac App Store** apps (out of scope for the collector).
- **Manual** installs (drag-drop to `/Applications`, vendor DMGs, non-brew CLI binaries not on `PATH` or not visible to `brew`).
- **Other** package managers (MacPorts, Cargo global installs, etc.) unless reflected in `paths` or user notes.

**Action:** Fill gaps via user interview or a short manual list in this section before locking Phase 1.

---

## 3. Phased rollout

### Phase 0 — Preconditions

- [ ] Backups, LUKS/disk plan documented
- [ ] Decide: stable vs unstable; unfree and CUDA if needed
- [ ] Hardware quirks (Wi‑Fi, Bluetooth, Apple Silicon–class power if relevant)

### Phase 1 — Minimal system

- [ ] `configuration.nix` / flake entry: networking, bootloader, users, `sudo`, SSH
- [ ] Core CLI aligned with inventory leaves where applicable
- [ ] **Replace brew intent:** for each important `homebrew.leaves` entry, map to a NixOS/Home Manager equivalent; do not plan to install Homebrew on NixOS

### Phase 2 — Developer toolchain

- [ ] Languages/runtimes (match leaves: e.g. Python, Rust, Node policy)
- [ ] Editors/LSP (match `paths` e.g. nvim)
- [ ] Containers/VM policy if Docker-like tools were used on macOS

### Phase 3 — Services and long-running workloads

- [ ] Databases, language servers as services, Ollama-style workloads if present
- [ ] Firewall and listening ports checklist

### Phase 4 — Desktop / GUI parity (optional)

- [ ] Map each important cask to: nix package, Flatpak, or “manual install” with rationale

---

## 4. Package mapping table

| macOS / Homebrew | NixOS approach | Notes |
|------------------|----------------|-------|
| _leaf or cask_ | _attribute or module_ | _unfree, version pin, alternative_ |

---

## 5. Verification

- [ ] `nix flake check` / `nixos-rebuild dry-build` succeeds
- [ ] CLI tools on `$PATH` smoke test
- [ ] Services start (`systemctl status …`)
- [ ] GUI spot-check for critical apps

---

## 6. Rollback and recovery

- **Bootloader generations:** how to select previous generation
- **Data:** what lives on impermanent vs persistent mounts
- **Secrets:** sops-nix, age, or agenix plan (no secrets in this repo)
- **Optional (macOS / nix-darwin experiments only):** If you previously used nix-darwin on a Mac, upstream documents uninstall via `darwin-uninstaller` / `nix run nix-darwin#darwin-uninstaller` — see [nix-darwin README](https://github.com/nix-darwin/nix-darwin). Not required for NixOS.

---

## 7. Follow-ups

- Items deferred from Phase 1–4
- Periodic drift review: compare `meta.inventoryDigest` from a new `collect-mac-state` run to the digest recorded when this playbook was written
