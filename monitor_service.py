#!/usr/bin/env python3
"""Background monitoring service for UpLite connections."""

import os
import sys
import time
import logging
from datetime import datetime

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from uplite.app import create_app, db
from uplite.models.connection import Connection
from uplite.utils.connection_checker import ConnectionChecker

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def monitor_all_connections():
    """Check all active connections and store results."""
    app = create_app()
    
    with app.app_context():
        # Get all active connections
        connections = Connection.query.filter_by(is_active=True).all()
        logger.info(f"Monitoring {len(connections)} active connections")
        
        checker = ConnectionChecker()
        
        for connection in connections:
            try:
                logger.info(f"Checking connection: {connection.name}")
                status, response_time, error = checker.check_connection(connection)
                
                # Update status (this will also store in history)
                connection.update_status(status, response_time, error)
                
                logger.info(f"Connection {connection.name}: {status} ({response_time}ms)")
                
            except Exception as e:
                logger.error(f"Error checking connection {connection.name}: {e}")
                connection.update_status('unknown', None, str(e))

def main():
    """Main monitoring loop."""
    logger.info("Starting UpLite monitoring service...")
    
    while True:
        try:
            monitor_all_connections()
            logger.info("Monitoring cycle completed, waiting 60 seconds...")
            time.sleep(60)  # Check every 60 seconds
            
        except KeyboardInterrupt:
            logger.info("Monitoring service stopped by user")
            break
        except Exception as e:
            logger.error(f"Error in monitoring service: {e}")
            time.sleep(10)  # Wait 10 seconds before retrying

if __name__ == '__main__':
    main()
