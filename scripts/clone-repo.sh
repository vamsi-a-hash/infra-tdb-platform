#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONFIG_FILE="$ROOT_DIR/local/repo.yaml"
TARGET_DIR="$(cd "$ROOT_DIR/.." && pwd)"

if ! command -v yq >/dev/null 2>&1; then
  echo "❌ yq is required (https://github.com/mikefarah/yq)"
  exit 1
fi

echo "📁 Cloning repositories into: $TARGET_DIR"

clone_repo() {
  local url="$1"
  local repo_name
  repo_name="$(basename "$url" .git)"
  local dest="$TARGET_DIR/$repo_name"

  if [ -d "$dest/.git" ]; then
    echo "✅ $repo_name already exists, skipping"
  else
    echo "⬇️  Cloning $repo_name..."
    git clone "$url" "$dest"
  fi
}

export -f clone_repo
export TARGET_DIR

yq -r '.repos[]' "$CONFIG_FILE" \
  | xargs -P 6 -n 1 bash -c 'clone_repo "$0"'
