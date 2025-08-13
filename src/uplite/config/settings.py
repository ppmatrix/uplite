"""Application configuration settings."""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Base configuration class."""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database settings
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if DATABASE_URL:
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    else:
        SQLALCHEMY_DATABASE_URI = (
            os.environ.get('SQLALCHEMY_DATABASE_URI') or
            'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), '../../uplite.db')
        )
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # UpLite specific settings
    DASHBOARD_REFRESH_INTERVAL = int(os.environ.get('DASHBOARD_REFRESH_INTERVAL', 30))  # seconds
    MAX_CONNECTION_TIMEOUT = int(os.environ.get('MAX_CONNECTION_TIMEOUT', 10))  # seconds
    ENABLE_REGISTRATION = os.environ.get('ENABLE_REGISTRATION', 'True').lower() == 'true'
    
    # Widget settings
    DEFAULT_WIDGETS = [
        'system_status',
        'connection_monitor',
        'service_status',
        'logs_viewer'
    ]
    
    # Monitoring settings
    PING_TIMEOUT = int(os.environ.get('PING_TIMEOUT', 5))  # seconds
    HTTP_TIMEOUT = int(os.environ.get('HTTP_TIMEOUT', 10))  # seconds
    CHECK_INTERVAL = int(os.environ.get('CHECK_INTERVAL', 60))  # seconds


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    TESTING = False


class TestingConfig(Config):
    """Testing configuration."""
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
