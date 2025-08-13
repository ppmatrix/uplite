"""API views for UpLite."""

from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user

from ..app import db
from ..models.connection import Connection
from ..models.widget_config import WidgetConfig
from ..utils.connection_checker import ConnectionChecker

bp = Blueprint('api', __name__)


@bp.route('/connections')
@login_required
def get_connections():
    """Get all connections with their status."""
    connections = Connection.query.filter_by(is_active=True).all()
    return jsonify([conn.to_dict() for conn in connections])


@bp.route('/connections/<int:connection_id>/status')
@login_required
def get_connection_status(connection_id):
    """Get status of a specific connection."""
    connection = Connection.query.get_or_404(connection_id)
    
    # Check connection status
    checker = ConnectionChecker()
    status, response_time, error = checker.check_connection(connection)
    
    # Update connection status
    connection.update_status(status, response_time, error)
    
    return jsonify(connection.to_dict())


@bp.route('/connections/<int:connection_id>/check', methods=['POST'])
@login_required
def check_connection(connection_id):
    """Manually trigger a connection check."""
    connection = Connection.query.get_or_404(connection_id)
    
    checker = ConnectionChecker()
    status, response_time, error = checker.check_connection(connection)
    
    # Update connection status
    connection.update_status(status, response_time, error)
    
    return jsonify({
        'status': status,
        'response_time': response_time,
        'error': error,
        'timestamp': connection.last_check.isoformat() if connection.last_check else None
    })


@bp.route('/widgets')
@login_required
def get_widgets():
    """Get user's widget configurations."""
    widgets = WidgetConfig.query.filter_by(
        user_id=current_user.id,
        is_enabled=True
    ).order_by(WidgetConfig.position).all()
    
    return jsonify([widget.to_dict() for widget in widgets])


@bp.route('/widgets/<int:widget_id>', methods=['PUT'])
@login_required
def update_widget(widget_id):
    """Update a widget configuration."""
    widget = WidgetConfig.query.filter_by(
        id=widget_id,
        user_id=current_user.id
    ).first_or_404()
    
    data = request.get_json()
    
    if 'config' in data:
        widget.update_config(data['config'])
    
    if 'position' in data:
        widget.update_position(data['position'])
    
    if 'is_enabled' in data:
        widget.is_enabled = data['is_enabled']
        db.session.commit()
    
    return jsonify(widget.to_dict())


@bp.route('/widgets/<int:widget_id>/data')
@login_required
def get_widget_data(widget_id):
    """Get data for a specific widget."""
    widget = WidgetConfig.query.filter_by(
        id=widget_id,
        user_id=current_user.id
    ).first_or_404()
    
    # Import widget manager to get widget data
    from ..widgets.widget_manager import WidgetManager
    
    widget_manager = WidgetManager()
    widget_data = widget_manager.get_widget_data(widget.widget_type, widget.config)
    
    return jsonify(widget_data)


@bp.route('/dashboard/refresh')
@login_required
def refresh_dashboard():
    """Refresh all dashboard data."""
    # Get all active connections
    connections = Connection.query.filter_by(is_active=True).all()
    
    # Check all connections
    checker = ConnectionChecker()
    updated_connections = []
    
    for connection in connections:
        status, response_time, error = checker.check_connection(connection)
        connection.update_status(status, response_time, error)
        updated_connections.append(connection.to_dict())
    
    return jsonify({
        'connections': updated_connections,
        'timestamp': connections[0].last_check.isoformat() if connections else None
    })


@bp.errorhandler(404)
def not_found(error):
    """Handle 404 errors for API endpoints."""
    return jsonify({'error': 'Not found'}), 404


@bp.errorhandler(400)
def bad_request(error):
    """Handle 400 errors for API endpoints."""
    return jsonify({'error': 'Bad request'}), 400


@bp.errorhandler(500)
def internal_error(error):
    """Handle 500 errors for API endpoints."""
    return jsonify({'error': 'Internal server error'}), 500

@bp.route('/connections', methods=['POST'])
@login_required
def add_connection():
    """Add a new connection."""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    required_fields = ['name', 'connection_type', 'target']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Validate connection type
    valid_types = ['http', 'ping', 'tcp', 'database']
    if data['connection_type'] not in valid_types:
        return jsonify({'error': f'Invalid connection type. Must be one of: {", ".join(valid_types)}'}), 400
    
    try:
        connection = Connection(
            name=data['name'],
            description=data.get('description'),
            connection_type=data['connection_type'],
            target=data['target'],
            port=data.get('port'),
            timeout=int(data.get('timeout', 10)),
            check_interval=int(data.get('check_interval', 60))
        )
        
        db.session.add(connection)
        db.session.commit()
        
        return jsonify(connection.to_dict()), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/connections/<int:connection_id>', methods=['PUT'])
@login_required
def update_connection(connection_id):
    """Update a connection."""
    connection = Connection.query.get_or_404(connection_id)
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    try:
        # Update allowed fields
        updateable_fields = ['connection_type', 'name', 'description', 'target', 'port', 'timeout', 'check_interval', 'is_active']
        for field in updateable_fields:
            if field in data:
                setattr(connection, field, data[field])
        
        db.session.commit()
        return jsonify(connection.to_dict())
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/connections/<int:connection_id>', methods=['DELETE'])
@login_required
def delete_connection(connection_id):
    """Delete a connection."""
    connection = Connection.query.get_or_404(connection_id)
    
    try:
        db.session.delete(connection)
        db.session.commit()
        return jsonify({'message': 'Connection deleted successfully'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/connections/<int:connection_id>')
@login_required
def get_connection(connection_id):
    """Get a single connection by ID."""
    connection = Connection.query.get_or_404(connection_id)
    return jsonify(connection.to_dict())
