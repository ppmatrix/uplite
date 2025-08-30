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
    # Get 1-hour statistics (use 1 day but only show last hour data)
    from datetime import datetime, timedelta
    cutoff_time = datetime.utcnow() - timedelta(hours=1)
    entries_1h = ConnectionHistory.query.filter(
        ConnectionHistory.connection_id == connection_id,
        ConnectionHistory.timestamp >= cutoff_time
    ).order_by(ConnectionHistory.timestamp.asc()).all()
    
    # Calculate 1-hour stats manually
    if entries_1h:
        total_checks = len(entries_1h)
        up_checks = sum(1 for e in entries_1h if e.status == 'up')
        uptime_percentage = (up_checks / total_checks * 100) if total_checks > 0 else 0
        
        valid_response_times = [e.response_time for e in entries_1h if e.response_time is not None and e.status == 'up']
        avg_response_time = sum(valid_response_times) / len(valid_response_times) if valid_response_times else None
        
        incidents_1h = ConnectionHistory._calculate_incidents(entries_1h)
        
        stats_1h = {
            'total_checks': total_checks,
            'uptime_percentage': round(uptime_percentage, 2),
            'avg_response_time': round(avg_response_time, 2) if avg_response_time else None,
            'incidents': incidents_1h,
            'period_start': cutoff_time,
            'period_end': datetime.utcnow()
        }
    else:
        stats_1h = {
            'total_checks': 0,
            'uptime_percentage': 0,
            'avg_response_time': None,
            'incidents': [],
            'period_start': cutoff_time,
            'period_end': datetime.utcnow()
        }
    
    return render_template(
        'dashboard/connection_stats.html',
        connection=connection,
        stats_7d=stats_7d,
        stats_24h=stats_24h,
        stats_1h=stats_1h,
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
    cutoff_time = datetime.utcnow() - timedelta(days=7)
    entries = ConnectionHistory.query.filter_by(connection_id=connection_id)\
                                   .filter(ConnectionHistory.timestamp >= cutoff_time)\
                                   .order_by(ConnectionHistory.timestamp.asc())\
                                   .limit(200).all()
    
    # Show raw entries
    raw_data = []
    for entry in entries:  # Show chronologically (query is already asc)
        raw_data.append({
            'timestamp': entry.timestamp.strftime('%m/%d %H:%M:%S'),
            'status': entry.status,
            'error': entry.error_message or 'None'
        })
    
    # Calculate incidents with our new method
    incidents = ConnectionHistory._calculate_incidents(entries)
    
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


@bp.route('/settings/profile', methods=['POST'])
@login_required
def update_profile():
    """Update user profile settings."""
    from flask import flash, redirect, url_for
    
    username = request.form.get('username', '').strip()
    email = request.form.get('email', '').strip()
    
    if not username or not email:
        flash('Username and email are required.', 'error')
        return redirect(url_for('dashboard.settings'))
    
    # Check if username is already taken by another user
    existing_user = db.session.query(db.exists().where(
        db.and_(
            current_user.__class__.username == username,
            current_user.__class__.id != current_user.id
        )
    )).scalar()
    
    if existing_user:
        flash('Username is already taken.', 'error')
        return redirect(url_for('dashboard.settings'))
    
    # Check if email is already taken by another user
    existing_email = db.session.query(db.exists().where(
        db.and_(
            current_user.__class__.email == email,
            current_user.__class__.id != current_user.id
        )
    )).scalar()
    
    if existing_email:
        flash('Email is already taken.', 'error')
        return redirect(url_for('dashboard.settings'))
    
    # Update profile
    current_user.username = username
    current_user.email = email
    
    try:
        db.session.commit()
        flash('Profile updated successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error updating profile. Please try again.', 'error')
    
    return redirect(url_for('dashboard.settings'))


@bp.route('/settings/password', methods=['POST'])
@login_required
def change_password():
    """Change user password."""
    from flask import flash, redirect, url_for
    
    current_password = request.form.get('current_password', '')
    new_password = request.form.get('new_password', '')
    confirm_password = request.form.get('confirm_password', '')
    
    # Validate inputs
    if not all([current_password, new_password, confirm_password]):
        flash('All password fields are required.', 'error')
        return redirect(url_for('dashboard.settings'))
    
    # Check current password
    if not current_user.check_password(current_password):
        flash('Current password is incorrect.', 'error')
        return redirect(url_for('dashboard.settings'))
    
    # Check new password length
    if len(new_password) < 8:
        flash('New password must be at least 8 characters long.', 'error')
        return redirect(url_for('dashboard.settings'))
    
    # Check password confirmation
    if new_password != confirm_password:
        flash('New passwords do not match.', 'error')
        return redirect(url_for('dashboard.settings'))
    
    # Update password
    current_user.set_password(new_password)
    
    try:
        db.session.commit()
        flash('Password changed successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error changing password. Please try again.', 'error')
    
    return redirect(url_for('dashboard.settings'))


@bp.route('/settings/app', methods=['POST'])
@login_required
def update_app_settings():
    """Update application settings."""
    from flask import flash, redirect, url_for, session
    
    theme = request.form.get('theme', 'light')
    refresh_interval = request.form.get('refresh_interval', '30')
    email_notifications = request.form.get('email_notifications') == 'on'
    
    # Validate refresh interval
    try:
        refresh_interval_int = int(refresh_interval)
        if refresh_interval_int < 5 or refresh_interval_int > 300:
            flash('Refresh interval must be between 5 and 300 seconds.', 'error')
            return redirect(url_for('dashboard.settings'))
    except ValueError:
        flash('Invalid refresh interval.', 'error')
        return redirect(url_for('dashboard.settings'))
    
    # Store settings in session (you could also create a UserSettings model)
    session['theme'] = theme
    session['refresh_interval'] = refresh_interval_int
    session['email_notifications'] = email_notifications
    
    flash('Settings saved successfully!', 'success')
    return redirect(url_for('dashboard.settings'))
