"""Connection monitoring history model for storing periodic check results."""

from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
from ..app import db
from statistics import median
from collections import defaultdict


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
        
        # Clean up old entries - keep 7 days of data instead of just 50 entries
        ConnectionHistory.cleanup_old_data(connection_id, retention_days=7)
        
        db.session.commit()
        return history_entry
    
    @staticmethod
    def cleanup_old_data(connection_id=None, retention_days=7):
        """Clean up old data beyond retention period."""
        cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
        query = ConnectionHistory.query.filter(ConnectionHistory.timestamp < cutoff_date)
        if connection_id:
            query = query.filter_by(connection_id=connection_id)
        
        deleted_count = query.count()
        if deleted_count > 0:
            query.delete()
            print(f"Cleaned up {deleted_count} old history entries for connection {connection_id or 'all'}")
    
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

    @staticmethod
    def get_connection_statistics(connection_id, days=7):
        """Get comprehensive statistics for a connection over the specified period."""
        cutoff_time = datetime.utcnow() - timedelta(days=days)
        entries = ConnectionHistory.query.filter(
            ConnectionHistory.connection_id == connection_id,
            ConnectionHistory.timestamp >= cutoff_time
        ).order_by(ConnectionHistory.timestamp.asc()).all()
        
        if not entries:
            return {
                'total_checks': 0,
                'uptime_percentage': 0,
                'avg_response_time': None,
                'incidents': [],
                'daily_stats': [],
                'period_start': cutoff_time,
                'period_end': datetime.utcnow()
            }
        
        # Calculate basic stats
        total_checks = len(entries)
        up_checks = sum(1 for e in entries if e.status == 'up')
        uptime_percentage = (up_checks / total_checks * 100) if total_checks > 0 else 0
        
        # Calculate average response time
        valid_response_times = [e.response_time for e in entries if e.response_time is not None and e.status == 'up']
        avg_response_time = sum(valid_response_times) / len(valid_response_times) if valid_response_times else None
        
        # Find incidents (periods of downtime)
        incidents = ConnectionHistory._calculate_incidents(entries)
        
        # Calculate daily statistics
        daily_stats = ConnectionHistory._calculate_daily_stats(entries, days)
        
        return {
            'total_checks': total_checks,
            'uptime_percentage': round(uptime_percentage, 2),
            'avg_response_time': round(avg_response_time, 2) if avg_response_time else None,
            'min_response_time': round(min(valid_response_times), 2) if valid_response_times else None,
            'max_response_time': round(max(valid_response_times), 2) if valid_response_times else None,
            'incidents': incidents,
            'daily_stats': daily_stats,
            'period_start': cutoff_time,
            'period_end': datetime.utcnow()
        }
    
    @staticmethod
    def _calculate_incidents(entries):
        """Calculate downtime incidents from history entries."""
        incidents = []
        current_incident = None
        
        for entry in entries:
            if entry.status == 'down' and current_incident is None:
                # Start of new incident
                current_incident = {
                    'start_time': entry.timestamp,
                    'end_time': None,
                    'duration_minutes': 0,
                    'error_message': entry.error_message
                }
            elif entry.status == 'up' and current_incident is not None:
                # End of current incident
                current_incident['end_time'] = entry.timestamp
                duration = current_incident['end_time'] - current_incident['start_time']
                current_incident['duration_minutes'] = round(duration.total_seconds() / 60, 1)
                current_incident['start_time_formatted'] = current_incident['start_time'].strftime('%b %d, %Y %H:%M')
                current_incident['end_time_formatted'] = current_incident['end_time'].strftime('%b %d, %Y %H:%M')
                incidents.append(current_incident)
                current_incident = None
        
        # Handle ongoing incident
        if current_incident is not None:
            current_incident['end_time'] = datetime.utcnow()
            duration = current_incident['end_time'] - current_incident['start_time']
            current_incident['duration_minutes'] = round(duration.total_seconds() / 60, 1)
            current_incident['ongoing'] = True
            current_incident['start_time_formatted'] = current_incident['start_time'].strftime('%b %d, %Y %H:%M')
            current_incident['end_time_formatted'] = None
            incidents.append(current_incident)
        
        return incidents
    
    @staticmethod
    def _calculate_daily_stats(entries, days):
        """Calculate daily statistics from history entries."""
        daily_data = defaultdict(lambda: {'up': 0, 'down': 0, 'response_times': []})
        
        for entry in entries:
            day_key = entry.timestamp.date()
            daily_data[day_key][entry.status] += 1
            if entry.response_time and entry.status == 'up':
                daily_data[day_key]['response_times'].append(entry.response_time)
        
        # Generate complete daily stats for the period
        daily_stats = []
        start_date = (datetime.utcnow() - timedelta(days=days)).date()
        
        for i in range(days):
            current_date = start_date + timedelta(days=i)
            day_data = daily_data[current_date]
            total_checks = day_data['up'] + day_data['down']
            uptime = (day_data['up'] / total_checks * 100) if total_checks > 0 else 0
            avg_response = sum(day_data['response_times']) / len(day_data['response_times']) if day_data['response_times'] else None
            
            daily_stats.append({
                'date': current_date.isoformat(),
                'date_formatted': current_date.strftime('%b %d, %a'),
                'total_checks': total_checks,
                'uptime_percentage': round(uptime, 1),
                'avg_response_time': round(avg_response, 2) if avg_response else None,
                'incidents_count': 1 if day_data['down'] > 0 else 0
            })
        
        return daily_stats
    
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
