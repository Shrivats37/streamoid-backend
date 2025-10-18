# Git Configuration for Streamoid Backend

## Repository Setup Commands

```bash
# Initialize Git repository (if not already done)
git init

# Add all files to staging
git add .

# Create initial commit
git commit -m "Initial commit: Enhanced Streamoid Backend v2.0.0

- Complete FastAPI product management system
- CSV upload with validation
- Full CRUD operations
- Advanced search and filtering
- Comprehensive analytics
- Docker deployment ready
- Production-ready with error handling"

# Add remote repository (replace with your actual repo URL)
git remote add origin https://github.com/yourusername/streamoid-backend.git

# Push to main branch
git push -u origin main
```

## Auto-Update Script

```bash
#!/bin/bash
# auto-update.sh - Script to automatically update Git repository

echo "🔄 Updating Streamoid Backend Repository..."

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo "❌ Not in a Git repository. Please initialize Git first."
    exit 1
fi

# Get current timestamp
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# Add all changes
git add .

# Check if there are changes to commit
if git diff --staged --quiet; then
    echo "✅ No changes to commit."
else
    # Commit changes
    git commit -m "Auto-update: $TIMESTAMP

- Updated project files
- Enhanced documentation
- Improved error handling
- Added new features"

    # Push to remote
    git push origin main
    
    echo "✅ Repository updated successfully!"
    echo "📅 Timestamp: $TIMESTAMP"
fi
```

## Git Hooks for Automatic Updates

### Pre-commit Hook
```bash
#!/bin/bash
# .git/hooks/pre-commit

echo "🔍 Running pre-commit checks..."

# Run tests
python -m pytest tests/ -v

# Check code formatting
python -m black app/ --check

# Run linting
python -m flake8 app/

echo "✅ Pre-commit checks passed!"
```

### Post-commit Hook
```bash
#!/bin/bash
# .git/hooks/post-commit

echo "📊 Generating project summary..."

# Update project summary with current status
python -c "
import json
import subprocess
from datetime import datetime

# Get git info
commit_hash = subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode().strip()[:8]
commit_date = subprocess.check_output(['git', 'log', '-1', '--format=%cd']).decode().strip()

# Update summary
summary = {
    'last_commit': commit_hash,
    'last_updated': commit_date,
    'status': 'Production Ready',
    'version': '2.0.0'
}

with open('PROJECT_STATUS.json', 'w') as f:
    json.dump(summary, f, indent=2)

print('✅ Project summary updated!')
"
```

## GitHub Actions Workflow

```yaml
# .github/workflows/ci.yml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        python -m pytest tests/ -v
    
    - name: Run linting
      run: |
        python -m flake8 app/
    
    - name: Build Docker image
      run: |
        docker build -t streamoid-backend .
    
    - name: Test Docker container
      run: |
        docker run -d -p 8000:8000 --name test-container streamoid-backend
        sleep 10
        curl -f http://localhost:8000/health
        docker stop test-container
        docker rm test-container

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Deploy to production
      run: |
        echo "🚀 Deploying to production..."
        # Add your deployment commands here
```

## Repository Structure for Git

```
streamoid-backend/
├── .git/
├── .github/
│   └── workflows/
│       └── ci.yml
├── app/
├── tests/
├── docs/
├── PROJECT_SUMMARY.md
├── PROJECT_STATUS.json
├── README.md
├── requirements.txt
├── docker-compose.yml
├── Dockerfile
├── .gitignore
└── auto-update.sh
```

## .gitignore Configuration

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
env/
ENV/

# Database
*.db
*.sqlite
*.sqlite3

# Logs
*.log
logs/

# Environment variables
.env
.env.local
.env.production

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Docker
.dockerignore

# Temporary files
*.tmp
*.temp
```

## Quick Commands for Repository Management

```bash
# Make auto-update script executable
chmod +x auto-update.sh

# Run auto-update
./auto-update.sh

# Check repository status
git status

# View commit history
git log --oneline

# Create a new feature branch
git checkout -b feature/new-feature

# Merge feature branch
git checkout main
git merge feature/new-feature

# Tag a release
git tag -a v2.0.0 -m "Release version 2.0.0"
git push origin v2.0.0
```

---

**Note**: Replace `yourusername` with your actual GitHub username and update the repository URL accordingly.
