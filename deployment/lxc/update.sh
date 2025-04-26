#!/bin/bash
set -e

ENV_FILE="$(dirname "$0")/env"
if [ ! -f "$ENV_FILE" ]; then
  echo "Missing environment file: $ENV_FILE"
  exit 1
fi

source "$ENV_FILE"

echo "=== Updating JB Filetools in Container ==="

echo "➡ Downloading latest wheel from GitHub Releases..."
pct exec "$CT_ID" -- bash -c "
  curl -fL -o /tmp/filetools-latest-py3-none-any.whl https://github.com/james-berkheimer/jb-filetools/releases/latest/download/filetools-latest-py3-none-any.whl
"

echo "➡ Installing updated wheel..."
pct exec "$CT_ID" -- bash -c "
  $VENV_PATH/bin/pip install --upgrade /tmp/filetools-latest-py3-none-any.whl
"

echo "➡ Cleaning up temporary files..."
pct exec "$CT_ID" -- bash -c "rm -f /tmp/filetools-*.whl"

echo "➡ Verifying filetools installation..."
pct exec "$CT_ID" -- bash -c "$VENV_PATH/bin/filetools --help"

echo "✅ JB Filetools successfully updated."
