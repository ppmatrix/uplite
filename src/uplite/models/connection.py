"""Connection model for monitoring services and endpoints."""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from ..app import db


class Connection(db.Model):
    """Model for storing connection/service monitoring information."""
    
    __tablename__ = 'connections'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    connection_type = db.Column(db.String(50), nullable=False)  # 'http', 'ping', 'tcp', 'database'
    target = db.Column(db.String(255), nullable=False)  # URL, IP, hostname, etc.
    port = db.Column(db.Integer)
    timeout = db.Column(db.Integer, default=10)  # seconds
    check_interval = db.Column(db.Integer, default=60)  # seconds
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Logo for visual identification
    logo_filename = db.Column(db.String(255))  # stores filename of uploaded logo
    
    # Status tracking
    last_check = db.Column(db.DateTime)
    last_status = db.Column(db.String(20))  # 'up', 'down', 'unknown'
    last_response_time = db.Column(db.Float)  # milliseconds
    last_error = db.Column(db.Text)
    
    # Configuration options (JSON)
    config_options = db.Column(db.JSON)
    
    def __init__(self, name, connection_type, target, **kwargs):
        """Initialize a new connection."""
        self.name = name
        self.connection_type = connection_type
        self.target = target
        
        # Set optional parameters
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def update_status(self, status, response_time=None, error=None):
        """Update the connection status and store historical data."""
        from .connection_history import ConnectionHistory
        
        self.last_check = datetime.utcnow()
        self.last_status = status
        self.last_response_time = response_time
        self.last_error = error
        self.updated_at = datetime.utcnow()
        
        # Store in history for median calculation
        ConnectionHistory.add_check_result(
            connection_id=self.id,
            status=status,
            response_time=response_time,
            error_message=error
        )
        
        db.session.commit()
    
    def get_median_response_time(self, periods=10):
        """Get median response time from the last N periods."""
        from .connection_history import ConnectionHistory
        return ConnectionHistory.get_median_response_time(self.id, periods)
    def get_chart_history(self, limit=20):
        """Get recent history for chart visualization."""
        from .connection_history import ConnectionHistory
        
        recent_entries = ConnectionHistory.query.filter_by(connection_id=self.id)\
            .order_by(ConnectionHistory.timestamp.desc())\
            .limit(limit).all()
        
        # Reverse to get chronological order (oldest first)
        recent_entries.reverse()
        
        return [entry.to_dict() for entry in recent_entries]
    
    def is_healthy(self):
        """Check if the connection is considered healthy."""
        return self.last_status == 'up'
    
    def get_status_color(self):
        """Get color class for status display."""
        status_colors = {
            'up': 'success',
            'down': 'danger',
            'unknown': 'warning'
        }
        return status_colors.get(self.last_status, 'secondary')
    
    def to_dict(self):
        """Convert connection to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'connection_type': self.connection_type,
            'target': self.target,
            'port': self.port,
            'timeout': self.timeout,
            'check_interval': self.check_interval,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_check': self.last_check.isoformat() if self.last_check else None,
            'last_status': self.last_status,
            'last_response_time': self.last_response_time,
            'median_response_time': self.get_median_response_time(),
            'last_error': self.last_error,
            'logo_filename': self.logo_filename,
            'config_options': self.config_options,
            'history': self.get_chart_history()
        }
    
    def __repr__(self):
        """String representation of the connection."""
        return f'<Connection {self.name} ({self.connection_type})>'
