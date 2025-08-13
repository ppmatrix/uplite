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
