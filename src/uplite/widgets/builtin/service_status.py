"""Service status widget for monitoring system services."""

import subprocess
import platform
from datetime import datetime
from typing import Dict, Any, List

from ..base_widget import BaseWidget


class ServiceStatusWidget(BaseWidget):
    """Widget to display system service status."""
    
    @property
    def widget_type(self) -> str:
        return 'service_status'
    
    @property
    def display_name(self) -> str:
        return 'Service Status'
    
    @property
    def description(self) -> str:
        return 'Monitor the status of system services'
    
    def get_data(self) -> Dict[str, Any]:
        """Get service status data."""
        try:
            services_to_monitor = self.config.get('services', self._get_default_services())
            
            service_statuses = []
            for service_name in services_to_monitor:
                status = self._get_service_status(service_name)
                service_statuses.append({
                    'name': service_name,
                    'status': status['status'],
                    'is_running': status['is_running'],
                    'is_enabled': status['is_enabled'],
                    'status_color': self._get_status_color(status['is_running'])
                })
            
            # Calculate summary
            total_services = len(service_statuses)
            running_services = sum(1 for s in service_statuses if s['is_running'])
            
            return {
                'services': service_statuses,
                'summary': {
                    'total': total_services,
                    'running': running_services,
                    'stopped': total_services - running_services,
                    'overall_status': 'success' if running_services == total_services else 'warning'
                },
                'timestamp': datetime.now().isoformat()
            }
        
        except Exception as e:
            return {
                'error': f'Failed to get service status: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }
    
    def _get_service_status(self, service_name: str) -> Dict[str, Any]:
        """Get status of a specific service."""
        try:
            if platform.system() == 'Linux':
                # Use systemctl for Linux
                result = subprocess.run(
                    ['systemctl', 'is-active', service_name],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                is_running = result.returncode == 0 and result.stdout.strip() == 'active'
                
                # Check if enabled
                result_enabled = subprocess.run(
                    ['systemctl', 'is-enabled', service_name],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                is_enabled = result_enabled.returncode == 0 and result_enabled.stdout.strip() == 'enabled'
                
                return {
                    'status': 'running' if is_running else 'stopped',
                    'is_running': is_running,
                    'is_enabled': is_enabled
                }
            else:
                # For non-Linux systems, return unknown
                return {
                    'status': 'unknown',
                    'is_running': False,
                    'is_enabled': False
                }
        
        except Exception:
            return {
                'status': 'error',
                'is_running': False,
                'is_enabled': False
            }
    
    def _get_default_services(self) -> List[str]:
        """Get default services to monitor based on the system."""
        if platform.system() == 'Linux':
            return ['nginx', 'apache2', 'mysql', 'postgresql', 'redis', 'docker']
        return []
    
    def _get_status_color(self, is_running: bool) -> str:
        """Get status color based on running state."""
        return 'success' if is_running else 'danger'
    
    @property
    def default_config(self) -> Dict[str, Any]:
        return {
            'refresh_interval': 60,
            'services': self._get_default_services()
        }
