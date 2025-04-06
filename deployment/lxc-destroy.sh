#!/bin/bash

if [ "$EUID" -ne 0 ]; then
  echo "Please run as root (sudo)"
  exit 1
fi


source "$(dirname "$0")/env.lxc"

echo "=== Stopping and destroying container ID: $CT_ID ==="
pct stop $CT_ID || true
pct destroy $CT_ID

echo "=== Container $CT_ID destroyed ==="
