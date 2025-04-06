#!/bin/bash

set -e

# Load env
source "$(dirname "$0")/env.lxc"

echo "=== Pulling latest JB Filetools code ==="
pct exec $CT_ID -- bash -c "cd $APP_PATH && git pull"

echo "=== Updating Python dependencies ==="
pct exec $CT_ID -- bash -c "$VENV_PATH/bin/pip install --upgrade pip wheel setuptools"
pct exec $CT_ID -- bash -c "$VENV_PATH/bin/pip install $APP_PATH"

echo "=== App update complete ==="
