"""API views for UpLite."""

from flask import Blueprint, jsonify, request

import os
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from flask_login import login_required, current_user

from ..app import db
from ..models.connection import Connection
from ..models.widget_config import WidgetConfig
from ..utils.connection_checker import ConnectionChecker


# Configuration for file uploads
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "images", "connections")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
MAX_FILE_SIZE = 2 * 1024 * 1024  # 2MB

def allowed_file(filename):
    """Check if file has allowed extension."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def handle_logo_upload(file):
    """Handle logo file upload and return filename or None."""
    if not file or file.filename == "":
        return None
    
    if not allowed_file(file.filename):
        raise ValueError("Invalid file type. Only PNG, JPG, JPEG, GIF allowed.")
    
    # Check file size
    file.seek(0, os.SEEK_END)
    file_length = file.tell()
    if file_length > MAX_FILE_SIZE:
        raise ValueError("File too large. Maximum size is 2MB.")
    file.seek(0)  # Reset file pointer
    
    # Generate secure filename
    filename = secure_filename(file.filename)
    # Add timestamp to avoid conflicts
    import time
    filename = f"{int(time.time())}_{filename}"
    
    # Create upload directory if it does not exist
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    # Save file
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(file_path)
    
    return filename

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

@bp.route("/connections", methods=["POST"])
@login_required
def add_connection():
    print(f"DEBUG: add_connection called, request.method={request.method}")  
    print(f"DEBUG: request.content_type={request.content_type}")
    print(f"DEBUG: request.form={dict(request.form)}")
    print(f"DEBUG: request.files={dict(request.files)}")
    """Add a new connection with optional logo upload."""
    # Handle both form data (with files) and JSON data (backward compatibility)
    if request.content_type and "multipart/form-data" in request.content_type:
        # Form data with possible file upload
        data = request.form.to_dict()
        logo_file = request.files.get("logo")
    else:
        # JSON data (backward compatibility)
        data = request.get_json()
        logo_file = None
    
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    required_fields = ["name", "connection_type", "target"]
    for field in required_fields:
        if not data.get(field):
            return jsonify({"error": f"Missing required field: {field}"}), 400
    
    # Validate connection type
    valid_types = ["http", "ping", "tcp", "database"]
    if data["connection_type"] not in valid_types:
        return jsonify({"error": f"Invalid connection type. Must be one of: {", ".join(valid_types)}"}), 400
    
    try:
        # Handle logo upload
        logo_filename = None
        if logo_file:
            logo_filename = handle_logo_upload(logo_file)
        
        connection = Connection(
            name=data["name"],
            description=data.get("description") or None,
            connection_type=data["connection_type"],
            target=data["target"],
            port=int(data["port"]) if data.get("port") else None,
            timeout=int(data.get("timeout", 10)),
            check_interval=int(data.get("check_interval", 60)),
            logo_filename=logo_filename
        )
        
        db.session.add(connection)
        db.session.commit()
        
        return jsonify(connection.to_dict()), 201
    
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
@bp.route("/connections/<int:connection_id>", methods=["PUT"])
@login_required
def update_connection(connection_id):
    """Update a connection with optional logo upload."""
    connection = Connection.query.get_or_404(connection_id)
    
    # Handle both form data (with files) and JSON data (backward compatibility)
    if request.content_type and "multipart/form-data" in request.content_type:
        # Form data with possible file upload
        data = request.form.to_dict()
        logo_file = request.files.get("logo")
    else:
        # JSON data (backward compatibility)
        data = request.get_json()
        logo_file = None
    
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    try:
        # Handle logo upload (if provided)
        if logo_file:
            # Delete old logo file if it exists
            if connection.logo_filename:
                old_file_path = os.path.join(UPLOAD_FOLDER, connection.logo_filename)
                if os.path.exists(old_file_path):
                    os.remove(old_file_path)
            
            # Upload new logo
            connection.logo_filename = handle_logo_upload(logo_file)
        
        # Update allowed fields
        updateable_fields = ["connection_type", "name", "description", "target", "port", "timeout", "check_interval", "is_active"]
        for field in updateable_fields:
            if field in data:
                value = data[field]
                # Convert string boolean values
                if field == "is_active":
                    value = value in ["true", "True", True, "1", 1]
                # Convert port to int if provided
                elif field == "port" and value:
                    value = int(value)
                # Convert timeout and check_interval to int
                elif field in ["timeout", "check_interval"] and value:
                    value = int(value)
                setattr(connection, field, value)
        
        db.session.commit()
        return jsonify(connection.to_dict())
    
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


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
