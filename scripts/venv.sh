#!/usr/bin/env bash
# Must be sourced: source scripts/venv.sh

# Guard against execution
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  echo "❌ This script must be sourced:"
  echo "   source scripts/venv.sh"
  return 1
fi

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONFIG_FILE="$ROOT_DIR/config/config.yaml"

DEFAULT_VENV_NAME=".venv"

# Resolve venv name
if command -v yq >/dev/null 2>&1 && [ -f "$CONFIG_FILE" ]; then
  VENV_NAME="$(yq -r '.python.venv_name // ""' "$CONFIG_FILE")"
  [ -z "$VENV_NAME" ] && VENV_NAME="$DEFAULT_VENV_NAME"
else
  VENV_NAME="$DEFAULT_VENV_NAME"
fi

VENV_PATH="$ROOT_DIR/../$VENV_NAME"

# Deactivate any existing venv
if [[ -n "${VIRTUAL_ENV:-}" ]]; then
  echo "🔄 Deactivating current virtualenv: $(basename "$VIRTUAL_ENV")"
  deactivate
fi

# Create venv if missing
if [ ! -d "$VENV_PATH" ]; then
  echo "📦 Creating virtualenv: $VENV_NAME"
  python3 -m venv "$VENV_PATH" || {
    echo "❌ Failed to create virtualenv"
    return 1
  }
fi

# Activate venv (THIS WAS THE BUG)
# shellcheck disable=SC1090
source "$VENV_PATH/bin/activate"

echo "🐍 Virtualenv activated: $VENV_NAME"
echo "📍 Python: $(which python)"
echo "🔢 Version: $(python --version)"
