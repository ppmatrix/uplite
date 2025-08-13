# UpLite

A lightweight, configurable web dashboard and connection watcher built with Flask and SQLAlchemy. UpLite provides a modular widget system for monitoring services, system resources, and connections with a clean, responsive UI.

## Features

- 🌐 **Connection Monitoring**: Monitor HTTP endpoints, ping hosts, TCP connections, and databases
- 📊 **System Monitoring**: Track CPU, memory, disk usage, and system information
- 🧩 **Modular Widgets**: Customizable dashboard with draggable widgets
- 👤 **User Authentication**: Secure login system with user management
- 🐳 **Docker Ready**: Easy deployment with Docker and Docker Compose
- 📱 **Responsive Design**: Works on desktop and mobile devices
- ⚡ **Real-time Updates**: Auto-refreshing dashboard with WebSocket support
- 🔧 **Configurable**: Extensive configuration options via environment variables

## Quick Start

### Using Docker Compose (Recommended)

1. Clone the repository:
```bash
git clone <repository-url>
cd uplite
```

2. Start the application:
```bash
# Development mode
docker-compose -f docker-compose.dev.yml up -d

# Production mode
docker-compose up -d
```

3. Access the application at `http://localhost:5001`

### Local Development with uv

1. Install dependencies:
```bash
uv sync
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. Initialize the database:
```bash
uv run flask db init
uv run flask db migrate -m "Initial migration"
uv run flask db upgrade
```

4. Run the application:
```bash
uv run uplite
```

## Configuration

UpLite can be configured via environment variables in the `.env` file:

### Flask Configuration
- `SECRET_KEY`: Secret key for session management (required in production)
- `FLASK_ENV`: Environment mode (`development`, `production`, `testing`)
- `FLASK_DEBUG`: Enable debug mode (`True`, `False`)

### Database Configuration
- `SQLALCHEMY_DATABASE_URI`: Database connection string
  - SQLite: `sqlite:///uplite.db` (default)
  - PostgreSQL: `postgresql://user:password@host:port/database`
  - MySQL: `mysql://user:password@host:port/database`

### Application Settings
- `DASHBOARD_REFRESH_INTERVAL`: Dashboard auto-refresh interval in seconds (default: 30)
- `MAX_CONNECTION_TIMEOUT`: Maximum timeout for connection checks in seconds (default: 10)
- `ENABLE_REGISTRATION`: Allow new user registration (`True`, `False`)

### Monitoring Settings
- `PING_TIMEOUT`: Timeout for ping checks in seconds (default: 5)
- `HTTP_TIMEOUT`: Timeout for HTTP checks in seconds (default: 10)
- `CHECK_INTERVAL`: Interval between automatic checks in seconds (default: 60)

## Widget System

UpLite includes several built-in widgets:

### System Status Widget
Monitors system resources including:
- CPU usage percentage
- Memory usage and availability
- Disk space utilization
- System uptime and boot time

### Connection Monitor Widget
Tracks the status of configured connections:
- HTTP/HTTPS endpoint monitoring
- Ping connectivity tests
- TCP port checks
- Database connection monitoring

### Service Status Widget
Monitors system services (Linux systemd):
- Service running status
- Service enabled status
- Automatic service discovery

### Logs Viewer Widget
Displays recent log entries from:
- System journal (journalctl)
- Log files (/var/log/*)
- Service-specific logs

## API Endpoints

### Authentication
- `POST /auth/login` - User login
- `POST /auth/register` - User registration
- `GET /auth/logout` - User logout

### Dashboard
- `GET /dashboard/` - Main dashboard page
- `GET /dashboard/connections` - Connection management
- `GET /dashboard/widgets` - Widget configuration

### API
- `GET /api/connections` - Get all connections
- `GET /api/connections/{id}/status` - Get connection status
- `POST /api/connections/{id}/check` - Manual connection check
- `GET /api/widgets` - Get user widgets
- `PUT /api/widgets/{id}` - Update widget configuration
- `GET /api/widgets/{id}/data` - Get widget data
- `GET /api/dashboard/refresh` - Refresh all dashboard data

## Development

### Project Structure
```
uplite/
├── src/uplite/           # Main application package
│   ├── models/           # Database models
│   ├── views/            # Flask blueprints/views
│   ├── widgets/          # Widget system
│   │   └── builtin/      # Built-in widgets
│   ├── auth/             # Authentication forms
│   ├── utils/            # Utility functions
│   ├── config/           # Configuration settings
│   ├── static/           # CSS, JS, images
│   └── templates/        # Jinja2 templates
├── tests/                # Test suite
├── docker/               # Docker configuration
├── docs/                 # Documentation
└── pyproject.toml        # Project configuration
```

### Running Tests
```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src/uplite

# Run specific test file
uv run pytest tests/test_app.py
```

### Code Quality
```bash
# Format code
uv run black src/ tests/

# Lint code
uv run flake8 src/ tests/

# Type checking
uv run mypy src/
```

## Deployment

### Docker Production Deployment

1. Create production environment file:
```bash
cp .env .env.prod
# Edit .env.prod with production settings
```

2. Deploy with Docker Compose:
```bash
docker-compose up -d
```

### Manual Deployment

1. Install dependencies:
```bash
uv sync --no-dev
```

2. Set production environment variables

3. Initialize database:
```bash
uv run flask db upgrade
```

4. Run with a WSGI server:
```bash
uv run gunicorn "src.uplite:create_app()" --bind 0.0.0.0:5000
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

If you encounter any issues or have questions:

1. Check the [documentation](docs/)
2. Search existing [issues](https://github.com/your-repo/uplite/issues)
3. Create a new issue if needed

## Roadmap

- [ ] WebSocket support for real-time updates
- [ ] Plugin system for custom widgets
- [ ] Advanced alerting and notifications
- [ ] Multi-tenancy support
- [ ] REST API for external integrations
- [ ] Mobile app companion
- [ ] Grafana integration
- [ ] Custom dashboards and themes
