#!/bin/bash

# Load configuration from .env file if exists
ENV_FILE=".env"
if [ -f "$ENV_FILE" ]; then
    source "$ENV_FILE"
else
    echo "No .env file found. Exiting."
    exit 1
fi

# Command-line overrides
while getopts "i:n:b:a:g:v:h" opt; do
  case $opt in
    i) CT_ID="$OPTARG";;
    n) CT_HOSTNAME="$OPTARG";;
    b) BRIDGE="$OPTARG";;
    a) CT_IP="$OPTARG";;
    g) GATEWAY="$OPTARG";;
    v) VLAN_ID="$OPTARG";;
    h)
      echo "Usage: install.sh [-i CT_ID] [-n HOSTNAME] [-b BRIDGE] [-a CT_IP] [-g GATEWAY] [-v VLAN_ID]"
      exit 0
      ;;
  esac
done

# Validate mandatory variables
: "${CT_ID:?CT_ID not set}"
: "${BRIDGE0:?BRIDGE0 not set}"
: "${BRIDGE1:?BRIDGE1 not set}"
: "${BRIDGE:?BRIDGE not set}"
: "${CT_IP:?CT_IP not set}"
: "${GATEWAY:?GATEWAY not set}"

echo "Using configuration:"
echo "Container ID: $CT_ID"
echo "Hostname: $CT_HOSTNAME"
echo "Bridge: $BRIDGE"
echo "IP Address: $CT_IP"
echo "Gateway: $GATEWAY"
echo "VLAN ID: ${VLAN_ID:-None}"

# Create the LXC container
echo "Creating LXC container ($CT_ID)..."
pct create $CT_ID $TEMPLATE \
    --hostname $CT_HOSTNAME \
    --cores 2 \
    --memory 2048 \
    --rootfs $CT_STORAGE \
    --net0 name=eth0,bridge=$BRIDGE,ip=$CT_IP,gw=$GATEWAY \
    --ostype ubuntu

# Mount host directory
echo "Mounting host directory..."
pct set $CT_ID -mp0 "$HOST_MOUNT,mp=$CONTAINER_MOUNT"

# Start container
echo "Starting container..."
pct start $CT_ID
sleep 5

# Install Python & Git
echo "Setting up container environment..."
pct exec $CT_ID -- bash -c "apt update && apt install -y software-properties-common"
pct exec $CT_ID -- bash -c "add-apt-repository -y ppa:deadsnakes/ppa && apt update"
pct exec $CT_ID -- bash -c "apt install -y python${PYTHON_VERSION} python${PYTHON_VERSION}-venv git"

# Clone repository
echo "Deploying JB Filetools..."
pct exec $CT_ID -- git clone "$REPO_URL" "$APP_PATH"

# Python Environment & Dependencies
echo "Configuring Python environment..."
pct exec $CT_ID -- bash -c "python${PYTHON_VERSION} -m venv $APP_PATH/venv"
pct exec $CT_ID -- bash -c "$APP_PATH/venv/bin/pip install --upgrade pip wheel setuptools"

# Install app from pyproject.toml
pct exec $CT_ID -- bash -c "$APP_PATH/venv/bin/pip install $APP_PATH"

# Copy user-editable settings
pct exec $CT_ID -- mkdir -p /root/.config/filetools
pct exec $CT_ID -- cp $APP_PATH/settings.json /root/.config/filetools/settings.json

# Set FILETOOLS_SETTINGS env var for root shell
pct exec $CT_ID -- bash -c "echo 'export FILETOOLS_SETTINGS=/root/.config/filetools/settings.json' >> /root/.bashrc"

echo "Deployment complete!"
