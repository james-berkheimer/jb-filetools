#!/bin/bash

set -e

ENV_FILE="$(dirname "$0")/env"
if [ ! -f "$ENV_FILE" ]; then
  echo "❌ Missing environment file: $ENV_FILE"
  echo "Make sure you've run: deployment/install.sh"
  exit 1
fi

source "$ENV_FILE"

echo "=== Pulling latest JB Filetools code ==="
pct exec "$CT_ID" -- bash -c "cd $APP_PATH && git pull"

echo "=== Updating Python dependencies ==="
pct exec "$CT_ID" -- bash -c "$VENV_PATH/bin/pip install --upgrade pip wheel setuptools"
pct exec "$CT_ID" -- bash -c "$VENV_PATH/bin/pip install --upgrade $APP_PATH"

echo "✅ App update complete."
