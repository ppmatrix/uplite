"""UpLite - A lightweight, configurable web dashboard and connection watcher."""

__version__ = "0.1.0"

from .app import create_app

def main():
    """Main entry point for the application."""
    app = create_app()
    app.run(debug=False, host='0.0.0.0', port=5001, use_reloader=False)

__all__ = ['create_app', 'main']
