#!/bin/bash
CT_ID=105

# Stop and destroy the container
echo "Stopping container $CT_ID..."
pct stop $CT_ID

echo "Destroying container $CT_ID..."
pct destroy $CT_ID

echo "Container destroyed."
