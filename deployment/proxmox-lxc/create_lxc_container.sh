#!/bin/bash

# Load the environment variables from .env
ENV_FILE=".env"
if [ ! -f "$ENV_FILE" ]; then
  echo "Error: .env file not found!"
  exit 1
fi
source "$ENV_FILE"

# Check if the required template is available, download if needed
echo "Checking LXC template..."
pveam update
if ! pveam list local | grep -q "ubuntu-22.04"; then
    echo "Downloading Ubuntu 22.04 template..."
    pveam download local ubuntu-22.04-standard_22.04-1_amd64.tar.zst
fi

# Create the LXC container
echo "Creating LXC container ID: $CT_ID..."
pct create $CT_ID $TEMPLATE \
    --hostname "$CT_HOSTNAME" \
    --cores "$CORES" \
    --memory "$RAM" \
    --rootfs "$CT_STORAGE" \
    --net0 name=eth0,bridge="$BRIDGE0",ip="$CT_IP0",gw="$GATEWAY" \
    --net1 name=eth1,bridge="$BRIDGE1",ip="$CT_IP1",mtu="$MTU1" \
    --ostype ubuntu

# Ensure the host NFS mount directories exist
echo "Ensuring host directories exist..."
mkdir -p "$HOST_MOUNT_SRC"
mkdir -p "$HOST_MOUNT_DEST"

# Mount source and destination directories into container
echo "Binding host directories into container..."
pct set $CT_ID -mp0 "$HOST_MOUNT_SRC,mp=$MOUNT_MEDIA_SRC"
pct set $CT_ID -mp1 "$HOST_MOUNT_DEST,mp=$MOUNT_MEDIA_DEST"

echo "Mounted host $HOST_MOUNT_SRC → container $MOUNT_MEDIA_SRC"
echo "Mounted host $HOST_MOUNT_DEST → container $MOUNT_MEDIA_DEST"

# Start container
echo "Starting container $CT_ID..."
pct start $CT_ID
sleep 5

# Verify container startup
echo "Container creation complete. Current status:"
pct status $CT_ID

# Post-setup: Install SSH and basic tools inside the container
echo "Installing SSH and editor tools inside container..."
pct exec $CT_ID -- apt update
pct exec $CT_ID -- apt install -y openssh-server sudo curl vim nano

# Enable SSH service
echo "Enabling and starting SSH service..."
pct exec $CT_ID -- apt update
pct exec $CT_ID -- apt install -y openssh-server sudo curl vim nano
pct exec $CT_ID -- systemctl enable ssh
pct exec $CT_ID -- systemctl restart ssh

# Ensure SSH config allows root login and password authentication
echo "Configuring SSH to allow root login..."
pct exec $CT_ID -- sed -i 's/^#\?PermitRootLogin.*/PermitRootLogin yes/' /etc/ssh/sshd_config
pct exec $CT_ID -- sed -i 's/^#\?PasswordAuthentication.*/PasswordAuthentication yes/' /etc/ssh/sshd_config
pct exec $CT_ID -- systemctl restart ssh

# Set root password for SSH login
echo "Setting root password..."
pct exec $CT_ID -- bash -c "echo root:$ROOT_PASSWORD | chpasswd"

# Set default working directory for root login
echo "Setting default working directory to $MOUNT_MEDIA_SRC..."
pct exec $CT_ID -- bash -c "echo 'cd $MOUNT_MEDIA_SRC' >> /root/.bashrc"


echo "Container setup complete."
echo
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "LXC container $CT_ID created and configured."
echo "You can now SSH into it with:"
echo "  ssh root@${CT_IP0%%/*}"
echo
echo "Or enter the container from Proxmox host with:"
echo "  sudo pct enter $CT_ID"
echo
echo "Inside the container, you can:"
echo "  - Run your Filetools app"
echo "  - Manage packages, users, or settings"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

