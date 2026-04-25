# !/usr/bin/env bash
# Run from anywhere: shallow-clone default (or passed) repo, write JSON, remove clone.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
if [[ -f .venv/bin/activate ]]; then
  # shellcheck source=/dev/null
  source .venv/bin/activate
fi
exec insight-scan-external-repo "$@"
