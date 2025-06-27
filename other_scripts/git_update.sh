# Save backup of local config
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

# Find common ancestor (base version)
BASE=$(git merge-base HEAD FETCH_HEAD)
BASE_CONFIG=$(mktemp)
git show "$BASE:config/config.json" > "$BASE_CONFIG"

# Merge the three versions
cp "$LOCAL_CONFIG" "$MERGE_BACKUP" # backup
git merge-file "$LOCAL_CONFIG" "$BASE_CONFIG" "$REPO_CONFIG"

# Save the merged result back to the repo
cp "$LOCAL_CONFIG" "$REPO_CONFIG"

# Make scripts executable
chmod u+x "$REPO_DIR/other_scripts/"*.sh

echo "✅ Update complete. config.json merged and saved to $CONFIG_REPO_PATH. !!Check config.json for confilcts"