#!/bin/bash

if [ "$EUID" -ne 0 ]; then
  echo "Please run as root (sudo)"
  exit 1
fi


set -e

# Load env
source "$(dirname "$0")/env.lxc"

echo "=== Checking LXC Template ==="
pveam update
TEMPLATE_NAME=$(basename "$TEMPLATE")

if ! pveam list local | grep -q "$TEMPLATE_NAME"; then
    echo "Downloading LXC template $TEMPLATE_NAME..."
    pveam download local "$TEMPLATE_NAME"
fi


echo "=== Creating LXC container ID: $CT_ID ==="
pct create $CT_ID $TEMPLATE \
    --hostname "$CT_HOSTNAME" \
    --cores "$CORES" \
    --memory "$RAM" \
    --rootfs "$CT_STORAGE" \
    --net0 name=eth0,bridge="$BRIDGE0",ip="$CT_IP0",gw="$GATEWAY" \
    --net1 name=eth1,bridge="$BRIDGE1",ip="$CT_IP1",mtu="$MTU1" \
    --ostype ubuntu

echo "=== Ensuring host directories exist ==="
mkdir -p "$HOST_MOUNT_SRC"
mkdir -p "$HOST_MOUNT_DEST"

echo "=== Binding host directories into container ==="
pct set $CT_ID -mp0 "$HOST_MOUNT_SRC,mp=$MOUNT_MEDIA_SRC"
pct set $CT_ID -mp1 "$HOST_MOUNT_DEST,mp=$MOUNT_MEDIA_DEST"

echo "=== Starting container $CT_ID ==="
pct start $CT_ID
sleep 5

echo "=== Installing SSH and basic tools in container ==="
pct exec $CT_ID -- apt update
pct exec $CT_ID -- apt install -y openssh-server sudo curl vim nano

echo "=== Enabling SSH service ==="
pct exec $CT_ID -- systemctl enable ssh
pct exec $CT_ID -- systemctl restart ssh

echo "=== Configuring SSH root login ==="
pct exec $CT_ID -- sed -i 's/^#\?PermitRootLogin.*/PermitRootLogin yes/' /etc/ssh/sshd_config
pct exec $CT_ID -- sed -i 's/^#\?PasswordAuthentication.*/PasswordAuthentication yes/' /etc/ssh/sshd_config
pct exec $CT_ID -- systemctl restart ssh

echo "=== Setting root password ==="
pct exec $CT_ID -- bash -c "echo root:$ROOT_PASSWORD | chpasswd"

echo "=== Configuring useful aliases ==="
pct exec $CT_ID -- bash -c "echo \"alias settings='nano /etc/filetools/settings.json'\" >> /root/.bashrc"
pct exec $CT_ID -- bash -c "echo \"alias appdir='cd /opt/jb-filetools'\" >> /root/.bashrc"
pct exec $CT_ID -- bash -c "echo \"alias transdir='cd /mnt/transmission'\" >> /root/.bashrc"
pct exec $CT_ID -- bash -c "echo \"alias filetools='/opt/jb-filetools/venv/bin/filetools'\" >> /root/.bashrc"

echo "=== Container $CT_ID created and configured ==="
echo "➡ Connect: ssh root@${CT_IP0%%/*}"
echo "➡ Aliases ready: settings, appdir, transdir, filetools"
echo "=== Done ==="
echo "=== Remember to set the root password ==="