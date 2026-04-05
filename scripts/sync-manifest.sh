#!/usr/bin/env bash
# Keep docs/config/master.yaml in sync with config/master.yaml (GitHub Pages reads docs/).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
mkdir -p "$ROOT/docs/config"
cp "$ROOT/config/master.yaml" "$ROOT/docs/config/master.yaml"
echo "Synced config/master.yaml -> docs/config/master.yaml"
