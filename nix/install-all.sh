#!/usr/bin/env bash
# Orchestrates satellite repos: clone (optional) and run each repo's nix/install.sh.
# DEVOPS_HORDE_ROOT is set by the flake app wrapper to this flake's source tree.
# Legacy MAIN_RELEASE_ROOT / MY_NIX_ROOT are still honored if DEVOPS_HORDE_ROOT is unset.
set -euo pipefail

resolve_root() {
  if [[ -n "${DEVOPS_HORDE_ROOT:-}" ]]; then
    printf '%s' "$DEVOPS_HORDE_ROOT"
    return
  fi
  if [[ -n "${MAIN_RELEASE_ROOT:-}" ]]; then
    printf '%s' "$MAIN_RELEASE_ROOT"
    return
  fi
  if [[ -n "${MY_NIX_ROOT:-}" ]]; then
    printf '%s' "$MY_NIX_ROOT"
    return
  fi
  local here
  here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  cd "$here/.."
  pwd
}

ROOT="$(resolve_root)"
MANIFEST="$ROOT/satellite-manifest.json"
SATELLITE_ROOT="${SATELLITE_ROOT:-$HOME/Code}"
CLONE_MISSING="${CLONE_MISSING:-1}"

if [[ ! -f "$MANIFEST" ]]; then
  echo "install-all: missing manifest: $MANIFEST" >&2
  exit 1
fi

if ! command -v jq &>/dev/null; then
  echo "install-all: jq is required (install jq or use: nix run .#install-all)" >&2
  exit 1
fi

while IFS=$'\t' read -r name gitUrl installScript; do
  [[ -z "$name" ]] && continue
  dest="$SATELLITE_ROOT/$name"
  if [[ ! -d "$dest/.git" ]]; then
    if [[ "$CLONE_MISSING" == "1" ]]; then
      echo "install-all: cloning $gitUrl -> $dest"
      mkdir -p "$SATELLITE_ROOT"
      git clone "$gitUrl" "$dest"
    else
      echo "install-all: skip (not cloned): $dest — set CLONE_MISSING=1 to clone" >&2
      continue
    fi
  fi
  script_path="$dest/${installScript:-nix/install.sh}"
  if [[ -f "$script_path" ]]; then
    echo "install-all: running $script_path"
    (cd "$dest" && bash "$script_path")
  else
    echo "install-all: skip (no script yet): $script_path"
  fi
done < <(jq -r '.satellites[] | [.name, .gitUrl, (.installScript // "nix/install.sh")] | @tsv' "$MANIFEST")

echo "install-all: done"
