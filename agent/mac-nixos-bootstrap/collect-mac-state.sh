#!/usr/bin/env bash
# Thin wrapper — implementation is collect-mac-state.py
# Debug: export COLLECT_MAC_STATE_DEBUG=1 or pass --debug / -d
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON="${PYTHON:-python3}"
exec "$PYTHON" "$DIR/collect-mac-state.py" "$@"
