"""Connection monitoring history model for storing periodic check results."""

from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
from ..app import db
from statistics import median


class ConnectionHistory(db.Model):
    """Model for storing historical connection monitoring data."""
    
    __tablename__ = 'connection_history'
    
    id = db.Column(db.Integer, primary_key=True)
    connection_id = db.Column(db.Integer, db.ForeignKey('connections.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    status = db.Column(db.String(20), nullable=False)  # 'up', 'down', 'unknown'
    response_time = db.Column(db.Float)  # milliseconds
    error_message = db.Column(db.Text)
    
    # Relationship
    connection = db.relationship('Connection', backref=db.backref('history', lazy=True, order_by='ConnectionHistory.timestamp.desc()'))
    
    def __init__(self, connection_id, status, response_time=None, error_message=None):
        """Initialize a new connection history entry."""
        self.connection_id = connection_id
        self.status = status
        self.response_time = response_time
        self.error_message = error_message
    
    @staticmethod
    def add_check_result(connection_id, status, response_time=None, error_message=None):
        """Add a new check result to history."""
        history_entry = ConnectionHistory(
            connection_id=connection_id,
            status=status,
            response_time=response_time,
            error_message=error_message
        )
        db.session.add(history_entry)
        
        # Clean up old entries - keep only last 50 entries per connection
        # This ensures we have enough data for median calculation while not storing too much
        old_entries = ConnectionHistory.query.filter_by(connection_id=connection_id)\
            .order_by(ConnectionHistory.timestamp.desc())\
            .offset(50).all()
        
        for entry in old_entries:
            db.session.delete(entry)
        
        db.session.commit()
        return history_entry
    
    @staticmethod
    def get_median_response_time(connection_id, periods=10):
        """Get median response time for the last N periods."""
        recent_entries = ConnectionHistory.query.filter(
            ConnectionHistory.connection_id == connection_id,
            ConnectionHistory.response_time.isnot(None),
            ConnectionHistory.status == 'up'  # Only consider successful checks
        ).order_by(ConnectionHistory.timestamp.desc()).limit(periods).all()
        
        if not recent_entries:
            return None
        
        response_times = [entry.response_time for entry in recent_entries]
        return median(response_times)
    
    @staticmethod
    def get_recent_status_counts(connection_id, hours=24):
        """Get status counts for the last N hours."""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        entries = ConnectionHistory.query.filter(
            ConnectionHistory.connection_id == connection_id,
            ConnectionHistory.timestamp >= cutoff_time
        ).all()
        
        status_counts = {'up': 0, 'down': 0, 'unknown': 0}
        for entry in entries:
            status_counts[entry.status] = status_counts.get(entry.status, 0) + 1
        
        return status_counts
    
    def to_dict(self):
        """Convert history entry to dictionary."""
        return {
            'id': self.id,
            'connection_id': self.connection_id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'status': self.status,
            'response_time': self.response_time,
            'error_message': self.error_message
        }
    
    def __repr__(self):
        """String representation of the history entry."""
        return f'<ConnectionHistory {self.connection_id} - {self.status} at {self.timestamp}>'
