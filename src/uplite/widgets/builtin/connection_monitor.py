"""Connection monitor widget for tracking service availability."""

from datetime import datetime
from typing import Dict, Any

from ..base_widget import BaseWidget
from ...models.connection import Connection
from ...models.connection_history import ConnectionHistory


class ConnectionMonitorWidget(BaseWidget):
    """Widget to display connection monitoring status."""
    
    @property
    def widget_type(self) -> str:
        return 'connection_monitor'
    
    @property
    def display_name(self) -> str:
        return 'Connection Monitor'
    
    @property
    def description(self) -> str:
        return 'Monitor the status of configured connections and services'
    
    def get_data(self) -> Dict[str, Any]:
        """Get connection monitoring data."""
        try:
            # Get all active connections
            connections = Connection.query.filter_by(is_active=True).all()
            
            # Count statuses
            total_connections = len(connections)
            up_count = sum(1 for conn in connections if conn.last_status == 'up')
            down_count = sum(1 for conn in connections if conn.last_status == 'down')
            unknown_count = sum(1 for conn in connections if conn.last_status == 'unknown')
            
            # Calculate overall health
            if total_connections == 0:
                overall_status = 'warning'
                overall_message = 'No connections configured'
            elif down_count == 0:
                overall_status = 'success'
                overall_message = 'All services are up'
            elif down_count == total_connections:
                overall_status = 'danger'
                overall_message = 'All services are down'
            else:
                overall_status = 'warning'
                overall_message = f'{down_count} service(s) down'
            
            # Get connection details with median response times
            connection_list = []
            for conn in connections:
                median_response_time = conn.get_median_response_time(periods=10)
                
                # Get recent historical data for charts (last 20 entries)
                recent_history = ConnectionHistory.query.filter_by(connection_id=conn.id)\
                    .order_by(ConnectionHistory.timestamp.desc())\
                    .limit(20).all()
                
                # Convert to chart format
                history_data = []
                for entry in reversed(recent_history):  # Reverse to get chronological order
                    history_data.append({
                        'timestamp': entry.timestamp.isoformat() if entry.timestamp else None,
                        'response_time': entry.response_time,
                        'status': entry.status
                    })
                
                connection_list.append({
                    'id': conn.id,
                    'name': conn.name,
                    'description': conn.description,
                    'type': conn.connection_type,
                    'target': conn.target,
                    'status': conn.last_status or 'unknown',
                    'response_time': conn.last_response_time,
                    'median_response_time': median_response_time,
                    'last_check': conn.last_check.isoformat() if conn.last_check else None,
                    'error': conn.last_error,
                    'status_color': conn.get_status_color(),
                    'history': history_data
                })
            
            return {
                'summary': {
                    'total': total_connections,
                    'up': up_count,
                    'down': down_count,
                    'unknown': unknown_count,
                    'overall_status': overall_status,
                    'overall_message': overall_message
                },
                'connections': connection_list,
                'timestamp': datetime.now().isoformat()
            }
        
        except Exception as e:
            return {
                'error': f'Failed to get connection data: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }
    
    @property
    def default_config(self) -> Dict[str, Any]:
        return {
            'refresh_interval': 60,
            'show_response_times': True,
            'max_connections_display': 10
        }
