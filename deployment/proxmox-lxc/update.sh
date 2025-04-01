#!/bin/bash

# Load environment variables
ENV_FILE=".env"
if [ ! -f "$ENV_FILE" ]; then
  echo "Error: .env file not found!"
  exit 1
fi
source "$ENV_FILE"

echo "Updating JB Filetools in container $CT_ID..."

# Pull latest changes from repo
pct exec $CT_ID -- bash -c "cd $APP_PATH && git pull"

# Reinstall app (in case dependencies have changed)
pct exec $CT_ID -- bash -c "$APP_PATH/venv/bin/pip install ."

echo "Update complete."
