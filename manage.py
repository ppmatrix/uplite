"""Management script for UpLite application."""

import os
import click
from flask.cli import with_appcontext
from src.uplite.app import create_app, db
from src.uplite.models.user import User
from src.uplite.models.connection import Connection
from src.uplite.models.connection_history import ConnectionHistory


def create_cli():
    """Create CLI application."""
    app = create_app()
    
    @app.cli.command()
    @with_appcontext
    def init_db():
        """Initialize the database."""
        db.create_all()
        click.echo('Initialized the database.')
    
    @app.cli.command()
    @with_appcontext
    def create_admin():
        """Create an admin user."""
        username = click.prompt('Admin username')
        email = click.prompt('Admin email')
        password = click.prompt('Admin password', hide_input=True)
        
        if User.query.filter_by(username=username).first():
            click.echo(f'User {username} already exists.')
            return
        
        admin = User(username=username, email=email, password=password)
        admin.is_admin = True
        db.session.add(admin)
        db.session.commit()
        
        click.echo(f'Created admin user: {username}')
    
    @app.cli.command()
    @with_appcontext
    def add_sample_connections():
        """Add sample connections for testing."""
        sample_connections = [
            {
                'name': 'Google',
                'description': 'Google homepage',
                'connection_type': 'http',
                'target': 'https://www.google.com',
                'timeout': 5
            },
            {
                'name': 'Local Database',
                'description': 'Local PostgreSQL database',
                'connection_type': 'database',
                'target': 'localhost',
                'port': 5432,
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
        click.echo('Added sample connections.')
    
    return app


if __name__ == '__main__':
    app = create_cli()
    app.run()
