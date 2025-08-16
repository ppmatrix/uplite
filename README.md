# UpLite - Lightweight Monitoring Dashboard

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/flask-3.0+-green.svg)](https://flask.palletsprojects.com/)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)

> A lightweight, configurable web dashboard for monitoring connections, system resources, and services with an intuitive widget-based interface.

## ✨ Features

### 🌐 Connection Monitoring
- **HTTP/HTTPS Endpoints** - Monitor web services with response time tracking
- **Ping Connectivity** - Network reachability testing with latency measurements
- **TCP Port Checks** - Verify service availability on specific ports
- **Database Connections** - Monitor database server connectivity
- **Historical Data** - Track connection performance over time with charts

### 📊 System Monitoring
- **CPU Usage** - Real-time processor utilization monitoring
- **Memory Statistics** - RAM usage, availability, and swap information
- **Disk Space** - Storage utilization across mounted filesystems
- **System Information** - Uptime, boot time, and system details
- **Process Monitoring** - Track running processes and resource usage

### 🧩 Widget System
- **Modular Design** - Add, remove, and configure widgets as needed
- **Drag & Drop Interface** - Reorder widgets on your dashboard (UI ready)
- **Real-time Updates** - Auto-refreshing data with configurable intervals
- **Responsive Layout** - Optimized for desktop, tablet, and mobile devices
- **Customizable Settings** - Per-widget configuration options

### 🔐 Security & Authentication
- **User Management** - Secure login system with user accounts
- **Session Security** - Protected routes and secure session handling
- **Registration Control** - Optional user registration with admin controls
- **Password Security** - Hashed password storage with secure practices

### 🐳 Deployment Options
- **Docker Ready** - Complete containerization with Docker Compose
- **Local Development** - Easy setup with Python virtual environments
- **Production Deployment** - WSGI server compatibility and configuration
- **Environment Configuration** - Flexible settings via environment variables

## 🚀 Quick Start

### Using Docker Compose (Recommended)

1. **Clone the repository:**
```bash
git clone https://github.com/ppmatrix/uplite.git
cd uplite
```

2. **Configure environment:**
```bash
cp .env.example .env
# Edit .env with your preferred settings
```

3. **Start the application:**
```bash
# Development mode with auto-reload
docker-compose -f docker-compose.dev.yml up -d

# Production mode
docker-compose up -d
```

4. **Access the dashboard:**
   - Open your browser to `http://localhost:5001`
   - Create your admin account on first visit

### Local Development Setup

1. **Install dependencies with uv:**
```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Sync dependencies
uv sync
```

2. **Configure environment:**
```bash
cp .env.example .env
# Edit .env file with your configuration
```

3. **Initialize the database:**
```bash
uv run python manage.py init-db
uv run python manage.py create-admin
```

4. **Start the services:**
```bash
# Start the web application
uv run python start_app.py &

# Start the monitoring service
uv run python monitor_service.py &
```

5. **Access the application:**
   - Navigate to `http://localhost:5002`
   - Login with your admin credentials

## 📋 Configuration

UpLite is configured through environment variables in your `.env` file:

### Application Settings
```bash
# Flask Configuration
SECRET_KEY=your-secret-key-here
FLASK_ENV=development
FLASK_DEBUG=True

# Database
SQLALCHEMY_DATABASE_URI=sqlite:///uplite.db
# For PostgreSQL: postgresql://user:pass@localhost/uplite
# For MySQL: mysql://user:pass@localhost/uplite
```

### Monitoring Settings
```bash
# Dashboard refresh interval (seconds)
DASHBOARD_REFRESH_INTERVAL=30

# Connection timeouts (seconds)
MAX_CONNECTION_TIMEOUT=10
PING_TIMEOUT=5
HTTP_TIMEOUT=10

# Monitoring check interval (seconds)
CHECK_INTERVAL=60
```

### User Management
```bash
# Allow new user registration
ENABLE_REGISTRATION=True

# Admin user settings (for initial setup)
ADMIN_USERNAME=admin
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=secure-password
```

## 🎯 Usage

### Managing Connections

1. **Add New Connections:**
   - Navigate to Dashboard → Connections
   - Click "Add Connection"
   - Choose connection type (HTTP, Ping, TCP, Database)
   - Configure connection parameters
   - Save and activate monitoring

2. **Monitor Status:**
   - View real-time status indicators on the main dashboard
   - Check response times and availability percentages
   - Review historical performance charts

### Configuring Widgets

1. **Widget Management:**
   - Access Dashboard → Widgets
   - Enable/disable available widgets
   - Configure widget-specific settings
   - Customize refresh intervals

2. **Available Widgets:**
   - **System Status**: CPU, memory, and disk usage
   - **Connection Monitor**: Network and service connectivity
   - **Service Status**: System service monitoring (Linux)
   - **Logs Viewer**: Recent system and application logs

### User Administration

1. **User Management:**
   - Admin users can manage other accounts
   - Create, modify, or disable user accounts
   - Set user permissions and roles

## 🏗️ Architecture

### Project Structure
```
uplite/
├── src/uplite/              # Main application package
│   ├── models/              # Database models
│   │   ├── user.py          # User authentication model
│   │   ├── connection.py    # Connection monitoring model
│   │   ├── widget_config.py # Widget configuration model
│   │   └── connection_history.py # Historical data model
│   ├── views/               # Flask routes and views
│   │   ├── dashboard.py     # Main dashboard routes
│   │   ├── auth.py          # Authentication routes
│   │   ├── api.py           # REST API endpoints
│   │   └── connections.py   # Connection management
│   ├── widgets/             # Widget system
│   │   ├── builtin/         # Built-in widget implementations
│   │   │   ├── system_status.py      # System monitoring
│   │   │   ├── connection_monitor.py # Connection tracking
│   │   │   ├── service_status.py     # Service monitoring
│   │   │   └── logs_viewer.py        # Log file viewing
│   │   ├── base_widget.py   # Widget base class
│   │   └── widget_manager.py # Widget management system
│   ├── auth/                # Authentication system
│   ├── config/              # Configuration management
│   ├── utils/               # Utility functions
│   ├── static/              # CSS, JavaScript, images
│   └── templates/           # Jinja2 HTML templates
├── tests/                   # Test suite
├── docker/                  # Docker configuration
├── docs/                    # Documentation
└── pyproject.toml          # Project configuration
```

### Technology Stack
- **Backend**: Python 3.12+ with Flask web framework
- **Database**: SQLAlchemy ORM with SQLite/PostgreSQL/MySQL support
- **Frontend**: Bootstrap 5, JavaScript, Chart.js for visualizations
- **Monitoring**: Custom monitoring service with configurable intervals
- **Deployment**: Docker and Docker Compose for containerization
- **Package Management**: uv for fast dependency management

## 📡 API Reference

### Authentication Endpoints
```bash
POST /auth/login          # User authentication
POST /auth/register       # User registration (if enabled)
GET  /auth/logout         # Session termination
```

### Dashboard Endpoints
```bash
GET  /dashboard/          # Main dashboard interface
GET  /dashboard/connections # Connection management page
GET  /dashboard/widgets   # Widget configuration page
```

### REST API
```bash
GET  /api/connections              # List all connections
GET  /api/connections/{id}/status  # Get connection status
POST /api/connections/{id}/check   # Trigger manual check
GET  /api/widgets                  # Get user widget configuration
PUT  /api/widgets/{id}             # Update widget settings
GET  /api/widgets/{id}/data        # Retrieve widget data
GET  /api/dashboard/refresh        # Refresh all dashboard data
```

### Widget Data API
```bash
GET  /api/widgets/system-status/data      # System metrics
GET  /api/widgets/connection-monitor/data # Connection statuses
GET  /api/widgets/service-status/data     # Service information
GET  /api/widgets/logs-viewer/data        # Recent log entries
```

## 🧪 Development

### Running Tests
```bash
# Install test dependencies
uv sync --group test

# Run the full test suite
uv run pytest

# Run with coverage reporting
uv run pytest --cov=src/uplite --cov-report=html

# Run specific test files
uv run pytest tests/test_models.py
uv run pytest tests/test_widgets.py
```

### Code Quality
```bash
# Format code with black
uv run black src/ tests/

# Lint with flake8
uv run flake8 src/ tests/

# Type checking with mypy
uv run mypy src/

# Sort imports
uv run isort src/ tests/
```

### Development Workflow
```bash
# Create feature branch
git checkout -b feature/amazing-feature

# Make changes and test
uv run pytest
uv run black src/
uv run flake8 src/

# Commit and push
git add .
git commit -m "Add amazing feature"
git push origin feature/amazing-feature
```

## 🚀 Production Deployment

### Docker Deployment
```bash
# Clone repository
git clone https://github.com/ppmatrix/uplite.git
cd uplite

# Create production environment
cp .env.example .env.prod
# Edit .env.prod with production settings

# Deploy with Docker Compose
docker-compose -f docker-compose.yml up -d

# Check logs
docker-compose logs -f
```

### Manual Deployment
```bash
# Install production dependencies
uv sync --no-dev

# Set environment variables
export FLASK_ENV=production
export SECRET_KEY="your-production-secret"

# Initialize database
uv run python manage.py init-db
uv run python manage.py create-admin

# Run with gunicorn
uv run gunicorn "src.uplite:create_app()" \
    --bind 0.0.0.0:5000 \
    --workers 4 \
    --timeout 30
```

### Environment Variables for Production
```bash
# Security
SECRET_KEY=your-very-secure-secret-key
FLASK_ENV=production
FLASK_DEBUG=False

# Database (use PostgreSQL for production)
SQLALCHEMY_DATABASE_URI=postgresql://user:pass@db-host:5432/uplite

# Performance
DASHBOARD_REFRESH_INTERVAL=30
CHECK_INTERVAL=60
```

## 🤝 Contributing

We welcome contributions from the community! Here's how to get started:

### Getting Started
1. Fork the repository on GitHub
2. Clone your fork locally
3. Create a new branch for your feature or bug fix
4. Make your changes and add tests
5. Ensure all tests pass and code is properly formatted
6. Push to your fork and submit a pull request

### Development Guidelines
- Follow PEP 8 style guidelines
- Write clear, descriptive commit messages
- Add tests for new functionality
- Update documentation as needed
- Keep pull requests focused and atomic

### Reporting Issues
- Use GitHub Issues to report bugs or request features
- Provide detailed information including:
  - Steps to reproduce
  - Expected vs actual behavior
  - System information (OS, Python version, etc.)
  - Relevant log files or error messages

## 📚 Documentation

- **[Installation Guide](docs/installation.md)** - Detailed setup instructions
- **[Configuration Reference](docs/configuration.md)** - All configuration options
- **[API Documentation](docs/api.md)** - Complete API reference
- **[Widget Development](docs/widgets.md)** - Creating custom widgets
- **[Deployment Guide](docs/deployment.md)** - Production deployment
- **[Development Setup](DEVELOPMENT.md)** - Development environment setup
- **[Monitoring Guide](MONITORING_GUIDE.md)** - Monitoring service details

## 🗺️ Roadmap

### Near-term Goals
- [ ] WebSocket support for real-time updates
- [ ] Enhanced drag-and-drop widget reordering
- [ ] Custom alert thresholds and notifications
- [ ] Export/import configuration settings
- [ ] Multi-language support (i18n)

### Future Enhancements
- [ ] Plugin system for third-party widgets
- [ ] Advanced user permissions and roles
- [ ] Integration with external monitoring systems
- [ ] Mobile companion app
- [ ] Grafana dashboard integration
- [ ] Custom themes and branding options

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

If you need help or have questions:

1. **Documentation**: Check the [docs/](docs/) directory for detailed guides
2. **GitHub Issues**: Search existing [issues](https://github.com/ppmatrix/uplite/issues) or create a new one
3. **Discussions**: Join the conversation in [GitHub Discussions](https://github.com/ppmatrix/uplite/discussions)
4. **Email**: Contact the maintainers at ppmatrixcsk@gmail.com

## 🏷️ Changelog

### Version 0.1.0 (Current)
- Initial release with core monitoring functionality
- Widget-based dashboard system
- Docker containerization support
- User authentication and management
- REST API for external integrations

See [CHANGELOG.md](CHANGELOG.md) for detailed version history.

---

**Crafted with precision for developers who value simplicity and reliability.**
