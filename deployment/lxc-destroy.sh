#!/bin/bash

source "$(dirname "$0")/env.lxc"

echo "=== Stopping and destroying container ID: $CT_ID ==="
pct stop $CT_ID || true
pct destroy $CT_ID

echo "=== Container $CT_ID destroyed ==="
