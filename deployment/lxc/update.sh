#!/bin/bash
set -e

echo "=== Updating JB Filetools in Container ==="

FILETOOLS_VERSION=$(grep -Po '^FILETOOLS_VERSION=\K.*' /etc/environment)
VENV_PATH="/opt/jb-filetools/venv"

if [ -z "$FILETOOLS_VERSION" ]; then
  echo "Error: FILETOOLS_VERSION not set in /etc/environment"
  exit 1
fi

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
