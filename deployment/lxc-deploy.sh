#!/bin/bash

set -e

# Ensure running as root
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root (sudo)"
  exit 1
fi

echo "=== JB Filetools LXC Deployment ==="

# Load environment variables
source "$(dirname "$0")/env.lxc"

# Step 1: Create container
echo "=== Step 1: Creating LXC container ==="
bash "$(dirname "$0")/lxc-create.sh"

# Step 2: Install app inside container
echo "=== Step 2: Installing Filetools application ==="
bash "$(dirname "$0")/app-install.sh"

echo "=== Deployment complete! ==="
echo "You can now connect:"
echo "  ssh root@${CT_IP0%%/*}"
echo
echo "After login, use:"
echo "  source /root/.bashrc"
echo "  settings   # to edit settings.json"
echo "  filetools  # to run the application"
echo "  transdir   # to enter transmission dir"
echo
echo "Happy file tooling!"
