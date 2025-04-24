#!/bin/bash

if [ "$EUID" -ne 0 ]; then
  echo "Please run as root (sudo)"
  exit 1
fi

set -e

ENV_FILE="$(dirname "$0")/env"
if [ ! -f "$ENV_FILE" ]; then
  echo "Missing environment file: $ENV_FILE"
  echo "This file should have been generated from env-template during setup."
  exit 1
fi

source "$ENV_FILE"
APP_VERSION=$(grep '^FILETOOLS_VERSION=' "$ENV_FILE" | cut -d= -f2)

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
    --ostype ubuntu \
    --nameserver "8.8.8.8"

echo "=== Ensuring host directories exist ==="
mkdir -p "$HOST_MOUNT_SRC"
mkdir -p "$HOST_MOUNT_DEST"

echo "=== Binding host directories into container ==="
pct set $CT_ID -mp0 "$HOST_MOUNT_SRC,mp=$MOUNT_MEDIA_SRC"
pct set $CT_ID -mp1 "$HOST_MOUNT_DEST,mp=$MOUNT_MEDIA_DEST"

echo "=== Starting container $CT_ID ==="
pct start $CT_ID
sleep 5

echo "=== Configuring network in container (manual setup) ==="
pct exec $CT_ID -- ip link set dev eth0 up
pct exec $CT_ID -- ip addr add "$CT_IP0" dev eth0
pct exec $CT_ID -- ip route add default via "$GATEWAY"
pct exec $CT_ID -- bash -c "echo 'nameserver 8.8.8.8' > /etc/resolv.conf"
pct exec $CT_ID -- bash -c "echo 'nameserver 8.8.4.4' >> /etc/resolv.conf"

echo "=== Installing Python $PYTHON_VERSION and tools in container ==="
pct exec $CT_ID -- bash -c "
  apt update &&
  apt install -y software-properties-common &&
  add-apt-repository -y ppa:deadsnakes/ppa &&
  apt update &&
  apt install -y python${PYTHON_VERSION} python${PYTHON_VERSION}-venv python${PYTHON_VERSION}-distutils openssh-server sudo curl vim nano git
"

echo "=== Enabling SSH service ==="
pct exec $CT_ID -- systemctl enable ssh
pct exec $CT_ID -- systemctl restart ssh

echo "=== Configuring SSH root login ==="
pct exec $CT_ID -- sed -i 's/^#\?PermitRootLogin.*/PermitRootLogin yes/' /etc/ssh/sshd_config
pct exec $CT_ID -- sed -i 's/^#\?PasswordAuthentication.*/PasswordAuthentication yes/' /etc/ssh/sshd_config
pct exec $CT_ID -- systemctl restart ssh

echo "=== Setting root password ==="
pct exec $CT_ID -- bash -c "echo root:$ROOT_PASSWORD | chpasswd"

echo "=== Cloning JB Filetools repository inside container ==="
pct exec $CT_ID -- git clone https://github.com/james-berkheimer/jb-filetools.git "$APP_PATH"

echo "=== Creating virtual environment and installing dependencies ==="
pct exec $CT_ID -- bash -c "
cd $APP_PATH &&
python${PYTHON_VERSION} -m venv $VENV_PATH &&
$VENV_PATH/bin/pip install --upgrade pip wheel setuptools &&
$VENV_PATH/bin/pip install .
"

echo "=== Adding update.sh script inside container ==="
pct exec $CT_ID -- bash -c "cat > $APP_PATH/update.sh << 'EOF'
#!/bin/bash
set -e

echo '=== Updating JB Filetools in Container ==='

cd $APP_PATH

echo '➡ Pulling latest code from git...'
git pull

echo '➡ Upgrading pip and installing dependencies...'
$VENV_PATH/bin/pip install --upgrade pip wheel setuptools
$VENV_PATH/bin/pip install --upgrade .

echo '✅ Update complete.'
EOF
"

pct exec $CT_ID -- chmod +x "$APP_PATH/update.sh"

echo "=== Configuring useful aliases ==="
pct exec $CT_ID -- bash -c "cat >> /root/.bashrc << EOF
alias update='$APP_PATH/update.sh'
alias settings='nano /etc/filetools/settings.json'
alias appdir='cd $APP_PATH'
alias transdir='cd $MOUNT_MEDIA_SRC'
alias filetools='$VENV_PATH/bin/filetools'
export APP_VERSION=$APP_VERSION
export FILETOOLS_SETTINGS='/etc/filetools/settings.json'
EOF
"

echo "=== Disabling PAM systemd session hooks to speed up SSH ==="
pct exec $CT_ID -- sed -i 's/^session\s*required\s*pam_systemd\.so/#&/' /etc/pam.d/sshd
pct exec $CT_ID -- sed -i 's/^session\s*optional\s*pam_systemd\.so/#&/' /etc/pam.d/common-session

echo "=== Container $CT_ID created and configured ==="
echo "➡ Connect: ssh root@${CT_IP0%%/*}"
echo "➡ Aliases ready: appdir, filetools, settings, transdir, update"
echo "=== Done ==="
echo "=== Remember to set the root password ==="
