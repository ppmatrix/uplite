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

def handle_logo_selection(logo_choice, logo_file=None):
    """Handle logo selection - either from apps_icons or file upload."""
    from ..utils.image_suggester import ImageSuggester
    
    # Priority 1: Handle file upload (backward compatibility)
    if logo_file and logo_file.filename and logo_file.filename != "":
        return handle_logo_upload(logo_file)
    
    # Priority 2: Handle icon selection from apps_icons
    if logo_choice:
        suggester = ImageSuggester()
        return suggester.copy_icon_to_connections(logo_choice)
    
    return None

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
        # Handle logo selection (from apps_icons) or upload
        logo_choice = data.get("logo_choice") or request.form.get("logo_choice")
        logo_filename = handle_logo_selection(logo_choice, logo_file)
        
        # Set logo_filename if we got one
        if logo_filename:
            connection.logo_filename = logo_filename
        
        # Auto-suggest icon if none provided
        if not logo_filename:
            from ..utils.image_suggester import ImageSuggester
            suggester = ImageSuggester()
            suggested_icon = suggester.suggest_image(
                data["name"], 
                data.get("description", ""), 
                data["target"], 
                data["connection_type"]
            )
            if suggested_icon:
                logo_filename = suggester.copy_icon_to_connections(suggested_icon)
        
        connection = Connection(
            name=data["name"].strip(),
            description=data.get("description", "").strip() or None,
            connection_type=data["connection_type"].strip(),
            target=data["target"].strip(),
            port=int(data["port"]) if data.get("port") and str(data["port"]).strip() else None,
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
        # Handle logo selection (from apps_icons) or upload
        logo_choice = data.get("logo_choice") or request.form.get("logo_choice")
        logo_filename = handle_logo_selection(logo_choice, logo_file)
        
        # Set logo_filename if we got one
        if logo_filename:
            connection.logo_filename = logo_filename
        
        
        # Update allowed fields
        updateable_fields = ["connection_type", "name", "description", "target", "port", "timeout", "check_interval", "is_active"]
        for field in updateable_fields:
            if field in data:
                value = data[field]
                # Strip whitespace for string fields
                if isinstance(value, str):
                    value = value.strip()
                # Convert string boolean values
                if field == "is_active":
                    value = value in ["true", "True", True, "1", 1]
                # Convert port to int if provided
                elif field == "port" and value:
                    value = int(value)
                # Convert timeout and check_interval to int
                elif field in ["timeout", "check_interval"] and value:
                    value = int(value)
                # Skip empty strings for optional fields
                elif field in ["description"] and not value:
                    value = None
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
    print(f"DEBUG: Delete request for connection ID: {connection_id}")
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

@bp.route('/images/suggest')
@login_required
def suggest_image():
    """Suggest an image based on connection details."""
    name = request.args.get('name', '')
    description = request.args.get('description', '')
    target = request.args.get('target', '')
    connection_type = request.args.get('connection_type', '')
    
    from ..utils.image_suggester import ImageSuggester
    
    suggester = ImageSuggester()
    suggestion = suggester.suggest_image(name, description, target, connection_type)
    
    return jsonify({
        'suggested_image': suggestion,
        'message': f'Found suggestion: {suggestion}' if suggestion else 'No suitable suggestion found'
    })


@bp.route('/images/search')
@login_required
def search_images():
    """Search for images based on query."""
    query = request.args.get('q', '')
    limit = int(request.args.get('limit', 20))
    
    from ..utils.image_suggester import ImageSuggester
    
    suggester = ImageSuggester()
    if query:
        results = suggester.search_icons(query, limit)
    else:
        # Return all available icons if no query
        all_icons = suggester.get_available_icons()
        results = [icon['filename'] for icon in all_icons[:limit]]
    
    return jsonify({
        'results': results,
        'total': len(results)
    })


@bp.route('/images/available')
@login_required
def get_available_images():
    """Get all available app icons."""
    from ..utils.image_suggester import ImageSuggester
    
    suggester = ImageSuggester()
    available_icons = suggester.get_available_icons()
    
    return jsonify({
        'icons': available_icons,
        'total': len(available_icons)
    })



@bp.route('/admin/cleanup-images', methods=['POST'])
@login_required
def cleanup_unused_images():
    """Clean up unused images in connections directory."""
    # This should probably have admin role check in a real app
    from ..utils.image_suggester import ImageSuggester
    
    # Get all currently used logo filenames
    used_filenames = []
    connections = Connection.query.filter(Connection.logo_filename.isnot(None)).all()
    for conn in connections:
        if conn.logo_filename:
            used_filenames.append(conn.logo_filename)
    
    # Cleanup unused files
    suggester = ImageSuggester()
    cleaned_count = suggester.cleanup_unused_connection_images(used_filenames)
    
    return jsonify({
        'message': f'Cleaned up {cleaned_count} unused image files',
        'cleaned_count': cleaned_count
    })
