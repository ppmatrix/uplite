"""Logs viewer widget for displaying recent log entries."""

import os
import subprocess
from datetime import datetime
from typing import Dict, Any, List

from ..base_widget import BaseWidget


class LogsViewerWidget(BaseWidget):
    """Widget to display recent log entries."""
    
    @property
    def widget_type(self) -> str:
        return 'logs_viewer'
    
    @property
    def display_name(self) -> str:
        return 'Logs Viewer'
    
    @property
    def description(self) -> str:
        return 'View recent log entries from system and application logs'
    
    def get_data(self) -> Dict[str, Any]:
        """Get recent log entries."""
        try:
            log_files = self.config.get('log_files', self._get_default_log_files())
            max_lines = self.config.get('max_lines', 50)
            
            logs = []
            for log_file in log_files:
                if isinstance(log_file, dict):
                    file_path = log_file.get('path')
                    file_name = log_file.get('name', os.path.basename(file_path))
                    file_type = log_file.get('type', 'file')
                else:
                    file_path = log_file
                    file_name = os.path.basename(file_path)
                    file_type = 'file'
                
                log_entries = self._read_log_file(file_path, file_type, max_lines)
                if log_entries:
                    logs.append({
                        'name': file_name,
                        'path': file_path,
                        'type': file_type,
                        'entries': log_entries,
                        'count': len(log_entries)
                    })
            
            return {
                'logs': logs,
                'total_entries': sum(log['count'] for log in logs),
                'timestamp': datetime.now().isoformat()
            }
        
        except Exception as e:
            return {
                'error': f'Failed to read logs: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }
    
    def _read_log_file(self, file_path: str, file_type: str, max_lines: int) -> List[str]:
        """Read log entries from a file or journal."""
        try:
            if file_type == 'journalctl':
                # Use journalctl for systemd journal
                result = subprocess.run(
                    ['journalctl', '-n', str(max_lines), '--no-pager'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0:
                    return result.stdout.strip().split('\n')
            
            elif file_type == 'service':
                # Use journalctl for specific service
                result = subprocess.run(
                    ['journalctl', '-u', file_path, '-n', str(max_lines), '--no-pager'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0:
                    return result.stdout.strip().split('\n')
            
            else:
                # Read regular file
                if os.path.exists(file_path) and os.access(file_path, os.R_OK):
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()
                        return [line.strip() for line in lines[-max_lines:] if line.strip()]
        
        except Exception:
            pass
        
        return []
    
    def _get_default_log_files(self) -> List[Dict[str, str]]:
        """Get default log files to monitor."""
        return [
            {'path': 'system', 'name': 'System Journal', 'type': 'journalctl'},
            {'path': '/var/log/syslog', 'name': 'System Log', 'type': 'file'},
            {'path': '/var/log/auth.log', 'name': 'Authentication Log', 'type': 'file'},
            {'path': 'nginx', 'name': 'Nginx Service', 'type': 'service'},
            {'path': 'apache2', 'name': 'Apache Service', 'type': 'service'}
        ]
    
    @property
    def default_config(self) -> Dict[str, Any]:
        return {
            'refresh_interval': 30,
            'max_lines': 50,
            'log_files': self._get_default_log_files()
        }
