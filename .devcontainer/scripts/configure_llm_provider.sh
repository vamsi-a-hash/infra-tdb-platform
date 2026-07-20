#!/usr/bin/env bash
# Interactive LLM provider + secrets setup, run once during DevPod
# post-create. Writes LLM_PROVIDER (and any secrets) into module-ttt/.env
# and/or Infisical, and drops a .secrets_mode marker that module-ttt's
# Makefile reads to decide how to load secrets at runtime.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEVCONTAINER_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
INFRA_DIR="$(cd "$DEVCONTAINER_DIR/.." && pwd)"
WORKSPACE="$(cd "$INFRA_DIR/.." && pwd)"
MODULE_DIR="$WORKSPACE/module-ttt"
ENV_FILE="$MODULE_DIR/.env"
SECRETS_MODE_FILE="$MODULE_DIR/.secrets_mode"

if [[ ! -d "$MODULE_DIR" ]]; then
  echo "⚠ module-ttt not found at $MODULE_DIR — skipping LLM provider setup."
  exit 0
fi

if [[ -r /dev/tty ]]; then TTY=/dev/tty; else TTY=; fi

ask() {
  # ask "prompt text" -> sets REPLY (empty if non-interactive)
  local prompt="$1"
  if [[ -z "$TTY" ]]; then
    REPLY=""
    return
  fi
  printf '%s' "$prompt" >&2
  read -r REPLY <"$TTY" || REPLY=""
}

# --------------------------------------------------------------- .env setup
if [[ ! -f "$ENV_FILE" && -f "$MODULE_DIR/.env.example" ]]; then
  echo "▶ Bootstrapping module-ttt/.env from .env.example"
  cp "$MODULE_DIR/.env.example" "$ENV_FILE"
fi
touch "$ENV_FILE"

set_var() {
  # set_var NAME VALUE -> upserts NAME=VALUE in $ENV_FILE
  local name="$1" value="$2"
  if grep -q "^${name}=" "$ENV_FILE" 2>/dev/null; then
    sed -i "s|^${name}=.*|${name}=${value}|" "$ENV_FILE"
  else
    echo "${name}=${value}" >> "$ENV_FILE"
  fi
}

# ------------------------------------------------------------- secrets mode
echo ""
echo "▶ How should secrets be managed?"
echo "  1) Infisical (recommended)"
echo "  2) .env file"
ask "Choose [1/2, default 1]: "
SECRETS_CHOICE="${REPLY:-1}"

SECRETS_MODE="dotenv"

if [[ "$SECRETS_CHOICE" == "1" ]]; then
  echo "▶ Setting up Infisical..."

  if ! command -v infisical >/dev/null 2>&1; then
    echo "  Installing Infisical CLI..."
    if curl -1sLf 'https://artifacts-cli.infisical.com/setup.deb.sh' | sudo -E bash >/dev/null 2>&1 \
       && sudo apt-get install -y -qq infisical >/dev/null 2>&1; then
      echo "  ✓ Infisical CLI installed"
    else
      echo "  ⚠ Infisical CLI install failed. Falling back to .env."
    fi
  fi

  if command -v infisical >/dev/null 2>&1; then
    echo "  Please log in to Infisical:"
    if infisical login <"$TTY" >&2; then
      SECRETS_MODE="infisical"
      echo "  ✓ Logged in to Infisical"
    else
      echo "  ⚠ Infisical login failed. Falling back to .env."
    fi
  fi
else
  echo "  Using .env for secrets."
fi

echo "$SECRETS_MODE" > "$SECRETS_MODE_FILE"

store_secret() {
  # store_secret NAME VALUE -> Infisical if configured, else .env
  local name="$1" value="$2"
  if [[ "$SECRETS_MODE" == "infisical" ]]; then
    if ! infisical secrets set "$name=$value" >/dev/null 2>&1; then
      echo "  ⚠ Failed to store $name in Infisical, writing to .env instead."
      set_var "$name" "$value"
    fi
  else
    set_var "$name" "$value"
  fi
}

# --------------------------------------------------------------- local/cloud
echo ""
echo "▶ Which LLM provider should this workspace use?"
echo "  1) Local (Qwen 3 4B via Ollama — recommended, runs on this machine)"
echo "  2) Cloud (OpenAI or Grok)"
ask "Choose [1/2, default 1]: "
PROVIDER_CHOICE="${REPLY:-1}"

if [[ "$PROVIDER_CHOICE" == "2" ]]; then
  echo ""
  echo "▶ Which cloud provider?"
  echo "  1) OpenAI (GPT-5.4-Mini)"
  echo "  2) Grok (Grok 4.3)"
  ask "Choose [1/2, default 1]: "
  CLOUD_CHOICE="${REPLY:-1}"

  if [[ "$CLOUD_CHOICE" == "2" ]]; then
    LLM_PROVIDER="grok"
    ask "  Enter your GROK_API_KEY: "
    store_secret "GROK_API_KEY" "$REPLY"
  else
    LLM_PROVIDER="openai"
    ask "  Enter your OPENAI_API_KEY: "
    store_secret "OPENAI_API_KEY" "$REPLY"
  fi

  set_var "LLM_PROVIDER" "$LLM_PROVIDER"
  echo "✔ Configured $LLM_PROVIDER as the LLM provider."

else
  LLM_PROVIDER="ollama"
  set_var "LLM_PROVIDER" "$LLM_PROVIDER"

  echo ""
  echo "▶ Setting up local model (Qwen 3 4B via Ollama)..."

  if ! command -v ollama >/dev/null 2>&1; then
    echo "  Installing Ollama..."
    curl -fsSL https://ollama.com/install.sh | sh
  fi

  echo "  Pulling qwen3:4b (this can take a few minutes)..."
  ollama pull qwen3:4b

  echo ""
  ask "  Is Ollama running somewhere other than http://localhost:11434? [y/N]: "
  if [[ "$REPLY" =~ ^[Yy] ]]; then
    ask "  Enter the OLLAMA_BASE_URL (e.g. http://host:port/v1): "
    set_var "OLLAMA_BASE_URL" "$REPLY"
  fi

  echo "✔ Configured Ollama (qwen3:4b) as the LLM provider."
fi

echo ""
echo "✔ LLM provider setup complete."