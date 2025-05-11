#!/bin/bash
set -e

VENV_PATH="/opt/jb-filetools/venv"
INSTALL_DIR="/opt/jb-filetools"

echo "=== Installing dependencies ==="
apt update
apt install -y python3 python3-venv python3-pip curl

echo "=== Creating installation directory ==="
mkdir -p "$VENV_PATH"

echo "=== Creating virtual environment ==="
python3 -m venv "$VENV_PATH"
"$VENV_PATH/bin/pip" install --upgrade pip setuptools wheel

echo "=== Downloading latest jb-filetools wheel ==="
LATEST_VERSION=$(curl -s https://api.github.com/repos/james-berkheimer/jb-filetools/releases/latest | grep -Po '"tag_name": "v\K[^"]+')
if [ -z "$LATEST_VERSION" ]; then
  echo "Error: Unable to fetch latest jb-filetools version from GitHub."
  exit 1
fi
curl -fL -o /tmp/filetools-${LATEST_VERSION}-py3-none-any.whl \
  "https://github.com/james-berkheimer/jb-filetools/releases/download/v${LATEST_VERSION}/filetools-${LATEST_VERSION}-py3-none-any.whl"

echo "=== Installing jb-filetools v${LATEST_VERSION} ==="
"$VENV_PATH/bin/pip" install /tmp/filetools-${LATEST_VERSION}-py3-none-any.whl
rm -f /tmp/filetools-*.whl

echo "=== Verifying install ==="
"$VENV_PATH/bin/filetools" --help

echo "=== Creating update.sh ==="
cat > "$INSTALL_DIR/update.sh" << 'EOF'
#!/bin/bash
set -e
VENV_PATH="/opt/jb-filetools/venv"
LATEST_VERSION=$(curl -s https://api.github.com/repos/james-berkheimer/jb-filetools/releases/latest | grep -Po '"tag_name": "v\K[^"]+')
if [ -z "$LATEST_VERSION" ]; then
  echo "Error: Unable to fetch latest jb-filetools version."
  exit 1
fi
echo "➡ Updating to version: $LATEST_VERSION"
curl -fL -o /tmp/filetools-${LATEST_VERSION}-py3-none-any.whl \
  "https://github.com/james-berkheimer/jb-filetools/releases/download/v${LATEST_VERSION}/filetools-${LATEST_VERSION}-py3-none-any.whl"
"$VENV_PATH/bin/pip" install --upgrade /tmp/filetools-${LATEST_VERSION}-py3-none-any.whl
rm -f /tmp/filetools-*.whl
"$VENV_PATH/bin/filetools" --help
echo "Update complete"
EOF

chmod +x "$INSTALL_DIR/update.sh"

echo "=== Creating uninstall.sh ==="
cat > "$INSTALL_DIR/uninstall.sh" << 'EOF'
#!/bin/bash
set -e
echo "Uninstalling JB Filetools..."
rm -rf /opt/jb-filetools
rm -f /usr/local/bin/filetools
rm -f /usr/local/bin/filetools_update
rm -f /usr/local/bin/filetools_uninstall
echo "JB Filetools has been removed."
EOF

chmod +x "$INSTALL_DIR/uninstall.sh"

echo "=== Creating symlinks in /usr/local/bin ==="
ln -sf "$VENV_PATH/bin/filetools" /usr/local/bin/filetools
ln -sf "$INSTALL_DIR/update.sh" /usr/local/bin/filetools_update
ln -sf "$INSTALL_DIR/uninstall.sh" /usr/local/bin/filetools_uninstall

echo "=== Installation complete ==="
echo "➡ Commands available: filetools, filetools_update, filetools_uninstall"
