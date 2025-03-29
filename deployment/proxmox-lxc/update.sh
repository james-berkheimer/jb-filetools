#!/bin/bash
CT_ID=105
APP_PATH="/opt/filetools"

# Pull latest changes
echo "Updating JB Filetools repository..."
pct exec $CT_ID -- bash -c "cd $APP_PATH && git pull"

# Update dependencies if requirements change
echo "Updating Python dependencies..."
pct exec $CT_ID -- bash -c "$APP_PATH/venv/bin/pip install --upgrade click colorlog"

echo "Update complete!"
