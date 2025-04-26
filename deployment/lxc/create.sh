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

echo "=== Checking LXC Template ==="
pveam update
TEMPLATE_NAME="$TEMPLATE"

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
  apt install -y python${PYTHON_VERSION} python${PYTHON_VERSION}-venv python3-pip openssh-server sudo curl vim nano git
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
$VENV_PATH/bin/pip install --upgrade pip setuptools wheel &&
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

echo "=== Setting up clean .bashrc ==="
pct exec $CT_ID -- bash -c "cat > /root/.bashrc << 'EOF'
# ~/.bashrc: executed by bash(1) for non-login shells.
[ -z \"\$PS1\" ] && return
HISTCONTROL=ignoredups:ignorespace
HISTSIZE=1000
HISTFILESIZE=2000
shopt -s histappend
shopt -s checkwinsize
[ -x /usr/bin/lesspipe ] && eval \"\$(SHELL=/bin/sh lesspipe)\"
if [ -z \"\$debian_chroot\" ] && [ -r /etc/debian_chroot ]; then
    debian_chroot=\$(cat /etc/debian_chroot)
fi
force_color_prompt=yes
if [ -n \"\$force_color_prompt\" ]; then
    if [ -x /usr/bin/tput ] && tput setaf 1 >&/dev/null; then
        color_prompt=yes
    else
        color_prompt=
    fi
fi
if [ \"\$color_prompt\" = yes ]; then
    PS1='\${debian_chroot:+(\$debian_chroot)}\[\e[1;32m\]\u@\h:\w\[\e[0m\]\$ '
else
    PS1='\${debian_chroot:+(\$debian_chroot)}\u@\h:\w\$ '
fi
unset color_prompt force_color_prompt
case \"\$TERM\" in
    xterm*|rxvt*)
        PS1=\"\[\e]0;\${debian_chroot:+(\$debian_chroot)}\u@\h: \w\a\]\$PS1\"
        ;;
esac
if [ -x /usr/bin/dircolors ]; then
    if [ -r ~/.dircolors ]; then
        eval \"\$(dircolors -b ~/.dircolors)\"
    else
        eval \"\$(dircolors -b)\"
    fi
fi
if [ -f ~/.bash_aliases ]; then
    . ~/.bash_aliases
fi
export GREP_COLOR='1;32'
EOF
"

echo "=== Creating .bash_aliases ==="
pct exec $CT_ID -- bash -c "cat > /root/.bash_aliases << 'EOF'
# ~/.bash_aliases
alias sbash='source .bashrc'
alias ..='cd ..'
alias ...='cd ../..'
alias ls='ls --color=auto'
alias ll='ls -alF --color=auto'
alias la='ls -A --color=auto'
alias l='ls -CF --color=auto'
alias grep='grep --color=auto'
alias fgrep='fgrep --color=auto'
alias egrep='egrep --color=auto'
alias cls='clear'
alias update='/opt/jb-filetools/update.sh'
alias settings='nano /opt/jb-filetools/venv/lib/python3.12/site-packages/filetools/settings.json'
alias appdir='cd /opt/jb-filetools'
alias transdir='cd /mnt/transmission'
alias filetools='/opt/jb-filetools/venv/bin/filetools'
EOF
"


echo "=== Setting global environment variables ==="
pct exec $CT_ID -- bash -c "echo 'FILETOOLS_SETTINGS=/opt/jb-filetools/venv/lib/python3.12/site-packages/filetools/settings.json' >> /etc/environment"
pct exec $CT_ID -- bash -c "echo 'APP_VERSION=$APP_VERSION' >> /etc/environment"

echo "=== Disabling PAM systemd session hooks to speed up SSH ==="
pct exec $CT_ID -- sed -i 's/^session\s*required\s*pam_systemd\.so/#&/' /etc/pam.d/sshd
pct exec $CT_ID -- sed -i 's/^session\s*optional\s*pam_systemd\.so/#&/' /etc/pam.d/common-session

echo "=== Container $CT_ID created and configured ==="
echo "➡ Connect: ssh root@${CT_IP0%%/*}"
echo "➡ Aliases ready: appdir, filetools, settings, transdir, update"
echo "=== Done ==="
echo "=== Remember to set the root password ==="
