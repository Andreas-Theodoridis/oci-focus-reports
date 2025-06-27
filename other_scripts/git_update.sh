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

echo "♻️ Merging local config.json with repo version..."
BASE=$(git merge-base HEAD FETCH_HEAD)
BASE_CONFIG=$(mktemp)

# Ensure base version is found
git show "$BASE:config/config.json" > "$BASE_CONFIG" || {
  echo "❌ Could not extract base config.json from Git"; exit 1;
}

cp "$LOCAL_CONFIG" "$MERGE_BACKUP" # backup before merge

# Merge local, base, and updated versions
git merge-file "$LOCAL_CONFIG" "$BASE_CONFIG" "$REPO_CONFIG"

# Save result back to repo
cp "$LOCAL_CONFIG" "$REPO_CONFIG"

# Make bash scripts executable if they exist
if compgen -G "$REPO_DIR/other_scripts/*.sh" > /dev/null; then
  chmod u+x "$REPO_DIR/other_scripts/"*.sh
else
  echo "⚠️ No .sh files found in other_scripts/"
fi

echo "✅ Update complete. config.json merged to $REPO_CONFIG"