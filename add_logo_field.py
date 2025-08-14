#!/usr/bin/env python3
"""
Migration script to add logo_filename field to existing connections table.
Run this once to update the database schema.
"""

import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from uplite.app import create_app, db
from sqlalchemy import text

def add_logo_field():
    """Add logo_filename column to connections table."""
    app = create_app()
    
    with app.app_context():
        try:
            # Check if column already exists
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            columns = [c['name'] for c in inspector.get_columns('connections')]
            
            if 'logo_filename' not in columns:
                # Add the column
                db.session.execute(text('ALTER TABLE connections ADD COLUMN logo_filename VARCHAR(255)'))
                db.session.commit()
                print("✅ Successfully added logo_filename column to connections table")
            else:
                print("ℹ️  logo_filename column already exists")
                
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error adding logo_filename column: {e}")
            return False
    
    return True

if __name__ == '__main__':
    print("🔄 Adding logo_filename field to connections table...")
    if add_logo_field():
        print("🎉 Migration completed successfully!")
    else:
        print("💥 Migration failed!")
        sys.exit(1)
