#!/bin/bash

REPO_DIR="/home/opc/oci-focus-reports"
LOCAL_CONFIG="/home/opc/config.json"
REPO_CONFIG="$REPO_DIR/config/config.json"
MERGE_BACKUP="/home/opc/config.json.bak"

echo "📁 Navigating to $REPO_DIR..."
cd "$REPO_DIR" || { echo "❌ Failed to enter directory"; exit 1; }

echo "📦 Stashing local changes..."
git stash save "Auto-stash before pulling latest changes"

echo "🔄 Fetching and updating from Git..."
git pull origin main

echo "🧹 Cleaning untracked files..."
git clean -fdX

echo "📄 Backing up local config.json..."
cp "$LOCAL_CONFIG" "$MERGE_BACKUP" || {
  echo "❌ Failed to backup local config"; exit 1;
}

echo "🔧 Merging repo and local config.json with jq..."
MERGED_CONFIG=$(mktemp)

# Merge: Git version first, then local overrides
jq -s '.[0] * .[1]' "$REPO_CONFIG" "$LOCAL_CONFIG" > "$MERGED_CONFIG" || {
  echo "❌ JSON merge failed"; exit 1;
}

echo "💾 Writing merged config to repo..."
cp "$MERGED_CONFIG" "$REPO_CONFIG"

# OPTIONAL: If you also want to save merged result back to local
# cp "$MERGED_CONFIG" "$LOCAL_CONFIG"

echo "🧼 Cleaning up temp file..."
rm "$MERGED_CONFIG"

# Make bash scripts executable if they exist
if compgen -G "$REPO_DIR/other_scripts/*.sh" > /dev/null; then
  chmod u+x "$REPO_DIR/other_scripts/"*.sh
else
  echo "⚠️ No .sh files found in other_scripts/"
fi

echo "✅ Update complete. config.json has been merged and saved to $REPO_CONFIG"