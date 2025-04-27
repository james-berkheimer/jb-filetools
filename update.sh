#!/bin/bash
set -e

echo "=== Updating JB Filetools in Container ==="

VENV_PATH="/opt/jb-filetools/venv"

# Get latest release version dynamically from GitHub API
FILETOOLS_VERSION=$(curl -s https://api.github.com/repos/james-berkheimer/jb-filetools/releases/latest | grep -Po '"tag_name": "v\K[^"]+')

if [ -z "$FILETOOLS_VERSION" ]; then
  echo "Error: Unable to fetch latest jb-filetools version from GitHub."
  exit 1
fi

echo "➡ Latest version detected: $FILETOOLS_VERSION"

echo "➡ Downloading JB Filetools v$FILETOOLS_VERSION wheel..."
curl -fL -o /tmp/filetools-${FILETOOLS_VERSION}-py3-none-any.whl \
  https://github.com/james-berkheimer/jb-filetools/releases/download/v${FILETOOLS_VERSION}/filetools-${FILETOOLS_VERSION}-py3-none-any.whl

echo "➡ Installing updated wheel..."
$VENV_PATH/bin/pip install --upgrade /tmp/filetools-${FILETOOLS_VERSION}-py3-none-any.whl

echo "➡ Cleaning up temporary files..."
rm -f /tmp/filetools-*.whl

echo "➡ Verifying filetools installation..."
$VENV_PATH/bin/filetools --help

echo "✅ JB Filetools successfully updated."
