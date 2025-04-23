#!/bin/bash

if [ "$EUID" -ne 0 ]; then
  echo "Please run as root (sudo)"
  exit 1
fi

set -e

ENV_FILE="$(dirname "$0")/env"
if [ ! -f "$ENV_FILE" ]; then
  echo "❌ Missing environment file: $ENV_FILE"
  echo "Make sure you've run: deployment/install.sh"
  exit 1
fi

source "$ENV_FILE"

echo "=== Stopping and destroying container ID $CT_ID ==="
pct stop "$CT_ID" || true
pct destroy "$CT_ID"
echo "✅ Container $CT_ID has been destroyed."
