# UpLite Development Guide

## Git Workflow

### Branches
- `main` - Production-ready code, stable releases
- `develop` - Development integration branch
- `feature/*` - Feature development branches
- `bugfix/*` - Bug fix branches

### Getting Started

1. **Clone and Setup**
   ```bash
   git clone /path/to/uplite
   cd uplite
   
   # Copy environment configuration
   cp .env.example .env
   # Edit .env with your local settings
   
   # Setup Python environment
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   # .venv\Scripts\activate    # Windows
   
   # Install dependencies
   uv sync
   ```

2. **Database Setup**
   ```bash
   # Initialize database
   python manage.py init-db
   
   # Create admin user
   python manage.py create-admin
   ```

3. **Start Development Server**
   ```bash
   # Start main application
   python start_app.py
   
   # Start monitoring service (separate terminal)
   python monitor_service.py
   ```

### Development Workflow

1. **Create Feature Branch**
   ```bash
   git checkout develop
   git pull origin develop  # If using remote
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes**
   - Write code
   - Test thoroughly
   - Update documentation if needed

3. **Commit Changes**
   ```bash
   git add .
   git commit -m "feat: add your feature description
   
   - Detailed description of changes
   - Any breaking changes noted
   - Related issue numbers"
   ```

4. **Merge to Develop**
   ```bash
   git checkout develop
   git merge feature/your-feature-name
   git branch -d feature/your-feature-name
   ```

5. **Release to Main**
   ```bash
   git checkout main
   git merge develop
   git tag v1.0.1  # Version tag
   ```

## Development Tools

### Database Management
```bash
# Reset database
rm uplite.db
python manage.py init-db
python manage.py create-admin

# Add sample connections
python manage.py add-sample-connections
```

### Testing
```bash
# Run tests
python -m pytest tests/

# Run with coverage
python -m pytest --cov=src tests/
```

### Code Quality
```bash
# Format code
python -m black src/

# Lint code  
python -m flake8 src/

# Type checking
python -m mypy src/
```

## Project Structure

```
uplite/
├── src/uplite/          # Main application package
│   ├── models/          # Database models
│   ├── views/           # Route handlers
│   ├── templates/       # HTML templates
│   ├── static/          # CSS, JS, images
│   ├── utils/           # Utility functions
│   └── widgets/         # Dashboard widgets
├── tests/               # Test files
├── docker/              # Docker configuration
├── .env.example         # Environment template
└── docs/                # Documentation
```

## Contributing

1. Follow the git workflow above
2. Write tests for new features
3. Update documentation
4. Use semantic commit messages:
   - `feat:` - New features
   - `fix:` - Bug fixes
   - `docs:` - Documentation changes
   - `style:` - Code style changes
   - `refactor:` - Code refactoring
   - `test:` - Test additions/changes
   - `chore:` - Maintenance tasks

## Deployment

### Docker
```bash
# Development
docker-compose -f docker-compose.dev.yml up

# Production  
docker-compose up -d
```

### Manual
```bash
# Install dependencies
uv sync --frozen

# Set production environment
export FLASK_ENV=production
export SECRET_KEY=your-production-secret-key

# Initialize database
python manage.py init-db
python manage.py create-admin

# Start services
python start_app.py &
python monitor_service.py &
```


## GitHub Integration

### Setting up GitHub Remote

1. **Create GitHub Repository** (on github.com):
   - Go to https://github.com/ppmatrix
   - Click "New Repository"
   - Repository name: `uplite`
   - Description: "UpLite - Connection Monitoring Dashboard"
   - Make it Public or Private as preferred
   - **Do NOT** initialize with README, .gitignore, or license (we have these already)

2. **Add Remote and Push** (SSH - Recommended):
   ```bash
   # Add GitHub as remote origin (SSH)
   git remote add origin git@github.com:ppmatrix/uplite.git
   
   # Push main branch
   git push -u origin main
   
   # Push develop branch  
   git push -u origin develop
   ```

3. **Alternative HTTPS Setup** (if SSH keys not configured):
   ```bash
   git remote add origin https://github.com/ppmatrix/uplite.git
   git push -u origin main
   git push -u origin develop
   ```

### SSH Key Setup (if needed)

If you get permission denied errors, you need to set up SSH keys:

```bash
# Generate SSH key (if you don't have one)
ssh-keygen -t ed25519 -C "ppmatrixcsk@gmail.com"

# Start SSH agent
eval "$(ssh-agent -s)"

# Add key to agent
ssh-add ~/.ssh/id_ed25519

# Copy public key to clipboard
cat ~/.ssh/id_ed25519.pub
```

Then add the public key to GitHub:
1. Go to GitHub → Settings → SSH and GPG keys
2. Click "New SSH key"  
3. Paste your public key and save

### GitHub Features to Enable

- **Issues** - For bug tracking and feature requests
- **Projects** - For kanban-style project management  
- **Actions** - For CI/CD (see `.github/workflows/` if added)
- **Security** - Dependabot for dependency updates
- **Pages** - For documentation hosting

### Collaboration Workflow

1. **Fork and Clone** (for contributors):
   ```bash
   # Fork the repository on GitHub, then:
   git clone git@github.com:your-username/uplite.git
   git remote add upstream git@github.com:ppmatrix/uplite.git
   ```

2. **Create Pull Request**:
   ```bash
   git checkout develop
   git checkout -b feature/my-feature
   # Make changes...
   git push origin feature/my-feature
   # Create PR on GitHub from feature branch to develop
   ```
