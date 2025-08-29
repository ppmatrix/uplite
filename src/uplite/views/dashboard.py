"""Dashboard views for UpLite."""

from flask import Blueprint, render_template, request, jsonify, abort
from flask_login import login_required, current_user

from ..app import db
from ..models.connection import Connection
from ..models.widget_config import WidgetConfig
from ..models.connection_history import ConnectionHistory
from ..widgets.widget_manager import WidgetManager

bp = Blueprint('dashboard', __name__)


@bp.route('/')
@login_required
def index():
    """Main dashboard page."""
    # Get user's widget configurations
    widget_configs = WidgetConfig.query.filter_by(
        user_id=current_user.id,
        is_enabled=True
    ).order_by(WidgetConfig.position).all()
    
    # If no widgets configured, create default ones
    if not widget_configs:
        widget_configs = _create_default_widgets(current_user.id)
    
    # Get connections for monitoring widgets - ORDER BY created_at for consistent display
    connections = Connection.query.filter_by(is_active=True).order_by(Connection.position).all()
    
    return render_template(
        'dashboard/index.html',
        widget_configs=widget_configs,
        connections=connections
    )


@bp.route('/connections')
@login_required
def connections():
    """Connections management page."""
    # ORDER BY created_at for consistent display
    connections = Connection.query.order_by(Connection.position).all()
    return render_template('dashboard/connections.html', connections=connections)


@bp.route('/connections/<int:connection_id>/statistics')
@login_required
def connection_statistics(connection_id):
    """Statistics page for a specific connection."""
    connection = Connection.query.get_or_404(connection_id)
    
    # Get statistics for different periods
    stats_7d = ConnectionHistory.get_connection_statistics(connection_id, days=7)
    stats_24h = ConnectionHistory.get_connection_statistics(connection_id, days=1)
    
    return render_template(
        'dashboard/connection_stats.html',
        connection=connection,
        stats_7d=stats_7d,
        stats_24h=stats_24h
    )


@bp.route('/widgets')
@login_required
def widgets():
    """Widget configuration page."""
    widget_configs = WidgetConfig.query.filter_by(user_id=current_user.id).all()
    available_widgets = WidgetManager.get_available_widgets()
    
    return render_template(
        'dashboard/widgets.html',
        widget_configs=widget_configs,
        available_widgets=available_widgets
    )


@bp.route('/settings')
@login_required
def settings():
    """User settings page."""
    return render_template('dashboard/settings.html')




@bp.route('/connections/<int:connection_id>/debug')
@login_required
def connection_debug(connection_id):
    """Debug endpoint to see connection data status."""
    connection = Connection.query.get_or_404(connection_id)
    debug_info = ConnectionHistory.get_debug_info(connection_id, days=7)
    
    from flask import jsonify
    return jsonify({
        'connection_name': connection.name,
        'debug_info': debug_info
    })

@bp.route('/connections/<int:connection_id>/create-sample-data')
@login_required  
def create_sample_data(connection_id):
    """Create sample data for testing purposes."""
    connection = Connection.query.get_or_404(connection_id)
    result = ConnectionHistory.create_sample_data(connection_id, days=7)
    
    from flask import jsonify
    return jsonify({
        'connection_name': connection.name,
        'result': result
    })

@bp.route('/connections/<int:connection_id>/debug-incidents')
@login_required  
def debug_incidents(connection_id):
    """Debug incident calculation in detail."""
    connection = Connection.query.get_or_404(connection_id)
    
    # Get recent entries for debugging
    from datetime import datetime, timedelta
    cutoff_time = datetime.utcnow() - timedelta(days=2)
    entries = ConnectionHistory.query.filter_by(connection_id=connection_id)\
                                   .filter(ConnectionHistory.timestamp >= cutoff_time)\
                                   .order_by(ConnectionHistory.timestamp.desc())\
                                   .limit(50).all()
    
    # Show raw entries
    raw_data = []
    for entry in reversed(entries):  # Show chronologically
        raw_data.append({
            'timestamp': entry.timestamp.strftime('%m/%d %H:%M:%S'),
            'status': entry.status,
            'error': entry.error_message or 'None'
        })
    
    # Calculate incidents with our new method
    incidents = ConnectionHistory._calculate_incidents(reversed(entries))
    
    # Show calculated incidents
    incident_data = []
    for i, incident in enumerate(incidents, 1):
        incident_data.append({
            'number': i,
            'status_types': incident['status_types'],
            'status_desc': incident['status_desc'],
            'duration_min': incident['duration_minutes'],
            'start': incident['start_time_formatted'],
            'end': incident.get('end_time_formatted', 'Ongoing'),
            'ongoing': incident.get('ongoing', False)
        })
    
    from flask import jsonify
    return jsonify({
        'connection_name': connection.name,
        'total_entries': len(raw_data),
        'total_incidents': len(incidents),
        'raw_entries': raw_data,
        'calculated_incidents': incident_data
    })


@login_required  
def create_sample_data(connection_id):
    """Create sample data for testing purposes."""
    connection = Connection.query.get_or_404(connection_id)
    result = ConnectionHistory.create_sample_data(connection_id, days=7)
    
    from flask import jsonify
    return jsonify({
        'connection_name': connection.name,
        'result': result
    })

def _create_default_widgets(user_id):
    """Create default widgets for a new user."""
    from ..config.settings import Config
    
    default_widgets = []
    for i, widget_type in enumerate(Config.DEFAULT_WIDGETS):
        widget_config = WidgetConfig(
            user_id=user_id,
            widget_type=widget_type,
            position=i,
            widget_title=_get_default_widget_title(widget_type)
        )
        db.session.add(widget_config)
        default_widgets.append(widget_config)
    
    db.session.commit()
    return default_widgets


def _get_default_widget_title(widget_type):
    """Get default title for a widget type."""
    titles = {
        'system_status': 'System Status',
        'connection_monitor': 'Connection Monitor',
        'service_status': 'Service Status',
        'logs_viewer': 'Logs Viewer'
    }
    return titles.get(widget_type, widget_type.replace('_', ' ').title())
