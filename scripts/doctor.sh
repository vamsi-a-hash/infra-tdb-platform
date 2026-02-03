#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONFIG_FILE="$ROOT_DIR/config/config.yaml"

if ! command -v yq >/dev/null 2>&1; then
  echo "❌ yq is required"
  exit 1
fi

MIN_PYTHON=$(yq -r '.python.min_version' "$CONFIG_FILE")
VENV_NAME=$(yq -r '.python.venv_name' "$CONFIG_FILE")
VENV_PATH="$ROOT_DIR/../$VENV_NAME"

echo "🩺 TalkingDB Doctor Check"
echo "-------------------------"

# Check python
if ! command -v python3 >/dev/null 2>&1; then
  echo "❌ python3 not found"
  exit 1
fi

PYTHON_VERSION=$(python3 - <<EOF
import sys
print(f"{sys.version_info.major}.{sys.version_info.minor}")
EOF
)

if [[ "$(printf '%s\n' "$MIN_PYTHON" "$PYTHON_VERSION" | sort -V | head -n1)" != "$MIN_PYTHON" ]]; then
  echo "❌ Python $PYTHON_VERSION found, but >= $MIN_PYTHON required"
  exit 1
fi

echo "✅ Python version OK ($PYTHON_VERSION)"

# Check venv
if [ -d "$VENV_PATH" ]; then
  echo "✅ Virtualenv exists ($VENV_NAME)"
else
  echo "⚠️  Virtualenv not found ($VENV_NAME)"
fi
