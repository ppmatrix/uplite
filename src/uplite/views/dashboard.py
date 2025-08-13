"""Dashboard views for UpLite."""

from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user

from ..app import db
from ..models.connection import Connection
from ..models.widget_config import WidgetConfig
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
    
    # Get connections for monitoring widgets
    connections = Connection.query.filter_by(is_active=True).all()
    
    return render_template(
        'dashboard/index.html',
        widget_configs=widget_configs,
        connections=connections
    )


@bp.route('/connections')
@login_required
def connections():
    """Connections management page."""
    connections = Connection.query.all()
    return render_template('dashboard/connections.html', connections=connections)


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
