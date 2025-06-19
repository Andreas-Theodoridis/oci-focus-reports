#!/bin/bash

# Set working directory
REPO_DIR="/home/opc/oci-focus-reports"
CONFIG_BACKUP="/home/opc/config.json"
CONFIG_REPO_PATH="$REPO_DIR/config/config.json"

echo "📁 Navigating to $REPO_DIR..."
cd "$REPO_DIR" || { echo "❌ Failed to enter directory"; exit 1; }

echo "📦 Stashing local changes..."
git stash save "Auto-stash before pulling latest changes"

echo "🔄 Fetching and updating from Git..."
git pull origin main

echo "🧹 Ignoring any extra local directories..."
# Ensure untracked directories don't cause issues
git clean -fdX

echo "♻️ Restoring config.json from backup..."
cp "$CONFIG_BACKUP" "$CONFIG_REPO_PATH"

echo "Making bash scripts executable"
chmod u+x /home/opc/oci-focus-reports/other_scripts/*.sh

echo "✅ Update complete. config.json restored to $CONFIG_REPO_PATH"