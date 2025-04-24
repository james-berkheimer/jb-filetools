#!/bin/bash

set -e

cd "$(dirname "$0")"

ENV_FILE="lxc/env"

echo "=== JB Filetools LXC Installer ==="

# Step 1: Ensure env file exists
if [ ! -f "$ENV_FILE" ]; then
    echo "No environment file found at $ENV_FILE"
    echo "Creating a template for you..."
    cp common/env-template "$ENV_FILE"
    echo "Please review and edit the file before continuing:"
    echo "  nano $ENV_FILE"
    exit 1
fi

# Step 2: Confirm user has edited the env file
echo
echo "Current container ID setting: $(grep '^CT_ID=' $ENV_FILE)"
read -p "Proceed with this container setup? [y/N] " confirm
if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
    echo "Cancelled."
    exit 0
fi

# Step 3: Run container creation and app install
echo
echo "=== Creating LXC Container ==="
bash lxc/create.sh

echo
echo "=== Installing JB Filetools into container ==="
bash lxc/install.sh

# Step 4: Wrap up
echo
echo "All done!"
source "$ENV_FILE"
echo "You can now SSH into your container:"
echo "  ssh root@${CT_IP0%%/*}"
echo
echo "Then run:"
echo "  update     # to pull latest JB Filetools changes"
echo "  filetools  # to use the CLI"
