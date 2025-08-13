"""Flask application factory and configuration."""

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

from .config.settings import Config

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()


def create_app(config_class=Config):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize Flask extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    
    # Configure login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    # Import models to ensure they are registered with SQLAlchemy
    from . import models
    
    # Register blueprints
    from .views.main import bp as main_bp
    app.register_blueprint(main_bp)
    
    from .views.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    from .views.dashboard import bp as dashboard_bp
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    
    from .views.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    return app


@login_manager.user_loader
def load_user(user_id):
    """Load a user by ID for Flask-Login."""
    from .models.user import User
    return User.query.get(int(user_id))
