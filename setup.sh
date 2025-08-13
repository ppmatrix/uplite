#!/bin/bash
# UpLite Setup Script

set -e

echo "🚀 Setting up UpLite..."

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ uv is not installed. Please install uv first:"
    echo "   curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
uv sync

# Initialize database
echo "🗄️  Initializing database..."
uv run python -c "
from src.uplite.app import create_app, db
app = create_app()
with app.app_context():
    db.create_all()
    print('✅ Database initialized!')
"

# Create admin user if requested
read -p "🔐 Do you want to create an admin user? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Creating admin user..."
    read -p "Username: " username
    read -p "Email: " email
    read -s -p "Password: " password
    echo
    
    uv run python -c "
from src.uplite.app import create_app, db
from src.uplite.models.user import User

app = create_app()
with app.app_context():
    if User.query.filter_by(username='$username').first():
        print('❌ User already exists!')
    else:
        user = User(username='$username', email='$email', password='$password')
        user.is_admin = True
        db.session.add(user)
        db.session.commit()
        print('✅ Admin user created!')
"
fi

# Add sample connections if requested
read -p "📡 Do you want to add sample connections? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Adding sample connections..."
    uv run python -c "
from src.uplite.app import create_app, db
from src.uplite.models.connection import Connection

app = create_app()
with app.app_context():
    sample_connections = [
        {
            'name': 'Google',
            'description': 'Google homepage',
            'connection_type': 'http',
            'target': 'https://www.google.com',
            'timeout': 5
        },
        {
            'name': 'GitHub',
            'description': 'GitHub API',
            'connection_type': 'http',
            'target': 'https://api.github.com',
            'timeout': 10
        },
        {
            'name': 'Localhost Ping',
            'description': 'Ping localhost',
            'connection_type': 'ping',
            'target': '127.0.0.1',
            'timeout': 3
        }
    ]
    
    for conn_data in sample_connections:
        if not Connection.query.filter_by(name=conn_data['name']).first():
            conn = Connection(**conn_data)
            db.session.add(conn)
    
    db.session.commit()
    print('✅ Sample connections added!')
"
fi

echo ""
echo "🎉 UpLite setup complete!"
echo ""
echo "To start the application:"
echo "  uv run uplite"
echo ""
echo "Or use Docker:"
echo "  docker-compose -f docker-compose.dev.yml up"
echo ""
echo "Access the application at: http://localhost:5001"
