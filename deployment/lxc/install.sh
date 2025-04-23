#!/bin/bash

set -e

# Load env
source "$(dirname "$0")/env.lxc"

echo "=== Setting up container environment ==="
pct exec $CT_ID -- bash -c "apt update && apt install -y python3.12 python3.12-venv git"

echo "=== Cloning JB Filetools repo ==="
pct exec $CT_ID -- git clone "$REPO_URL" "$APP_PATH"

echo "=== Creating Python virtual environment ==="
pct exec $CT_ID -- python3.12 -m venv "$VENV_PATH"
pct exec $CT_ID -- bash -c "$VENV_PATH/bin/pip install --upgrade pip wheel setuptools"

echo "=== Installing JB Filetools ==="
pct exec $CT_ID -- bash -c "$VENV_PATH/bin/pip install $APP_PATH"

echo "=== Copying settings.json to /etc/filetools ==="
pct exec $CT_ID -- mkdir -p /etc/filetools
pct exec $CT_ID -- cp "$APP_PATH/settings.json" /etc/filetools/settings.json

echo "=== Exporting FILETOOLS_SETTINGS to .bashrc ==="
pct exec $CT_ID -- bash -c "echo 'export FILETOOLS_SETTINGS=$SETTINGS_PATH' >> /root/.bashrc"

echo "=== App install complete ==="
