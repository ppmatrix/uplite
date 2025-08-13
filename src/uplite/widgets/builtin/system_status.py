"""System status widget for monitoring server resources."""

import psutil
import platform
from datetime import datetime
from typing import Dict, Any

from ..base_widget import BaseWidget


class SystemStatusWidget(BaseWidget):
    """Widget to display system status information."""
    
    @property
    def widget_type(self) -> str:
        return 'system_status'
    
    @property
    def display_name(self) -> str:
        return 'System Status'
    
    @property
    def description(self) -> str:
        return 'Monitor CPU, memory, disk usage and system information'
    
    def get_data(self) -> Dict[str, Any]:
        """Get system status data."""
        try:
            # CPU information
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            # Memory information
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_total = self._bytes_to_gb(memory.total)
            memory_used = self._bytes_to_gb(memory.used)
            memory_available = self._bytes_to_gb(memory.available)
            
            # Disk information
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            disk_total = self._bytes_to_gb(disk.total)
            disk_used = self._bytes_to_gb(disk.used)
            disk_free = self._bytes_to_gb(disk.free)
            
            # System information
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            uptime = datetime.now() - boot_time
            
            return {
                'cpu': {
                    'percent': round(cpu_percent, 1),
                    'count': cpu_count,
                    'status': self._get_status_level(cpu_percent)
                },
                'memory': {
                    'percent': round(memory_percent, 1),
                    'total_gb': round(memory_total, 1),
                    'used_gb': round(memory_used, 1),
                    'available_gb': round(memory_available, 1),
                    'status': self._get_status_level(memory_percent)
                },
                'disk': {
                    'percent': round(disk_percent, 1),
                    'total_gb': round(disk_total, 1),
                    'used_gb': round(disk_used, 1),
                    'free_gb': round(disk_free, 1),
                    'status': self._get_status_level(disk_percent)
                },
                'system': {
                    'platform': platform.system(),
                    'release': platform.release(),
                    'boot_time': boot_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'uptime_days': uptime.days,
                    'uptime_hours': uptime.seconds // 3600,
                    'uptime_minutes': (uptime.seconds % 3600) // 60
                },
                'timestamp': datetime.now().isoformat()
            }
        
        except Exception as e:
            return {
                'error': f'Failed to get system status: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }
    
    def _bytes_to_gb(self, bytes_value):
        """Convert bytes to gigabytes."""
        return bytes_value / (1024 ** 3)
    
    def _get_status_level(self, percent):
        """Get status level based on percentage."""
        if percent < 70:
            return 'success'
        elif percent < 90:
            return 'warning'
        else:
            return 'danger'
    
    @property
    def default_config(self) -> Dict[str, Any]:
        return {
            'refresh_interval': 30,
            'show_details': True
        }
