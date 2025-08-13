"""Widget configuration model for user dashboard customization."""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from ..app import db


class WidgetConfig(db.Model):
    """Model for storing user widget configurations."""
    
    __tablename__ = 'widget_configs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    widget_type = db.Column(db.String(50), nullable=False)  # 'system_status', 'connection_monitor', etc.
    widget_title = db.Column(db.String(100))
    position = db.Column(db.Integer, default=0)  # Order on dashboard
    size = db.Column(db.String(20), default='medium')  # 'small', 'medium', 'large'
    is_enabled = db.Column(db.Boolean, default=True, nullable=False)
    
    # Widget-specific configuration (JSON)
    config = db.Column(db.JSON)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, user_id, widget_type, **kwargs):
        """Initialize a new widget configuration."""
        self.user_id = user_id
        self.widget_type = widget_type
        
        # Set optional parameters
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def update_config(self, config):
        """Update widget configuration."""
        self.config = config
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def update_position(self, position):
        """Update widget position."""
        self.position = position
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def to_dict(self):
        """Convert widget config to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'widget_type': self.widget_type,
            'widget_title': self.widget_title,
            'position': self.position,
            'size': self.size,
            'is_enabled': self.is_enabled,
            'config': self.config,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        """String representation of the widget config."""
        return f'<WidgetConfig {self.widget_type} for User {self.user_id}>'
