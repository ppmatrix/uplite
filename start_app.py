#!/usr/bin/env python3
import sys
sys.path.append('.')

from src.uplite.app import create_app

if __name__ == '__main__':
    app = create_app()
    print("✅ UpLite starting on http://localhost:5002")
    app.run(debug=False, host='0.0.0.0', port=5002, use_reloader=False)
