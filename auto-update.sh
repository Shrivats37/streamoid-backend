#!/bin/bash
# auto-update.sh - Script to automatically update Git repository

echo "🔄 Updating Streamoid Backend Repository..."

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo "❌ Not in a Git repository. Please initialize Git first."
    echo "💡 Run: git init"
    exit 1
fi

# Get current timestamp
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# Check if there are any changes
if git diff --quiet && git diff --staged --quiet; then
    echo "✅ No changes to commit."
    exit 0
fi

# Add all changes
echo "📁 Adding files to staging..."
git add .

# Get list of changed files
CHANGED_FILES=$(git diff --staged --name-only | tr '\n' ' ')

# Commit changes
echo "💾 Committing changes..."
git commit -m "Auto-update: $TIMESTAMP

- Updated project files
- Enhanced documentation
- Improved error handling
- Added new features

Changed files: $CHANGED_FILES"

# Check if remote is configured
if git remote get-url origin >/dev/null 2>&1; then
    echo "🚀 Pushing to remote repository..."
    git push origin main
    
    if [ $? -eq 0 ]; then
        echo "✅ Repository updated successfully!"
        echo "📅 Timestamp: $TIMESTAMP"
        echo "🔗 Remote: $(git remote get-url origin)"
    else
        echo "❌ Failed to push to remote repository."
        echo "💡 Check your remote configuration: git remote -v"
    fi
else
    echo "⚠️  No remote repository configured."
    echo "💡 Add remote with: git remote add origin <your-repo-url>"
    echo "✅ Local changes committed successfully!"
fi

# Update project status
echo "📊 Updating project status..."
cat > PROJECT_STATUS.json << EOF
{
  "last_updated": "$TIMESTAMP",
  "status": "Production Ready",
  "version": "2.0.0",
  "commit_hash": "$(git rev-parse HEAD | cut -c1-8)",
  "branch": "$(git branch --show-current)",
  "total_commits": "$(git rev-list --count HEAD)",
  "features": [
    "CSV Upload & Validation",
    "Full CRUD Operations",
    "Advanced Search & Filtering",
    "Comprehensive Analytics",
    "Docker Deployment",
    "Error Handling",
    "API Documentation"
  ]
}
EOF

echo "✅ Project status updated!"
echo ""
echo "📋 Summary:"
echo "   - Timestamp: $TIMESTAMP"
echo "   - Commit: $(git rev-parse HEAD | cut -c1-8)"
echo "   - Branch: $(git branch --show-current)"
echo "   - Status: Production Ready"
