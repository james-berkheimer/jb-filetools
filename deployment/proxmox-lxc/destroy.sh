#!/bin/bash

# Load the environment variables from .env
ENV_FILE=".env"
if [ ! -f "$ENV_FILE" ]; then
  echo "Error: .env file not found!"
  exit 1
fi
source "$ENV_FILE"

# Prompt before destroying
read -p "Are you sure you want to destroy container $CT_ID? This action is irreversible! [y/N] " confirm
if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
  echo "Aborted."
  exit 1
fi

# Stop the container if running
echo "Stopping container $CT_ID..."
pct stop $CT_ID

# Unmount custom mount points
echo "Unmounting $MOUNT_MEDIA_SRC and $MOUNT_MEDIA_DEST..."
pct set $CT_ID -delete mp0
pct set $CT_ID -delete mp1

# Destroy the container
echo "Destroying container $CT_ID..."
pct destroy $CT_ID

echo "Container $CT_ID destroyed."
