# Updated functions for handling icon selection from apps_icons directory

def handle_logo_selection(logo_choice, logo_file=None):
    """Handle logo selection - either from apps_icons or file upload.
    
    Args:
        logo_choice: Selected icon filename from apps_icons directory
        logo_file: Uploaded file (FileStorage object)
        
    Returns:
        Filename in connections directory or None
    """
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
