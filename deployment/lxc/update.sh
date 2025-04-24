#!/bin/bash
set -e

ENV_FILE="$(dirname "$0")/env"
if [ ! -f "$ENV_FILE" ]; then
  echo "Missing environment file: $ENV_FILE"
  exit 1
fi

source "$ENV_FILE"

echo "=== Checking current JB Filetools version ==="
LOCAL_VERSION=$(pct exec "$CT_ID" -- bash -c "cat $APP_PATH/VERSION")
REMOTE_VERSION=$(git ls-remote https://github.com/james-berkheimer/jb-filetools.git HEAD | cut -f1)

echo "➡ Local version: $LOCAL_VERSION"
echo "➡ Remote commit: ${REMOTE_VERSION:0:7}"

# Check if repo is behind remote
NEEDS_UPDATE=$(pct exec "$CT_ID" -- bash -c "
  cd $APP_PATH &&
  LOCAL_COMMIT=\$(git rev-parse HEAD) &&
  [ \"\$LOCAL_COMMIT\" != \"$REMOTE_VERSION\" ] && echo yes || echo no
")

if [ "$NEEDS_UPDATE" != "yes" ]; then
  echo "Already up to date. No action taken."
  exit 0
fi

echo "⬇ Pulling latest code..."
pct exec "$CT_ID" -- bash -c "cd $APP_PATH && git pull"

echo "⬆ Updating Python dependencies..."
pct exec "$CT_ID" -- bash -c "$VENV_PATH/bin/pip install --upgrade pip wheel setuptools"
pct exec "$CT_ID" -- bash -c "$VENV_PATH/bin/pip install --upgrade $APP_PATH"

echo "JB Filetools updated to latest version."
