"""Connection checker utility for monitoring services."""

import socket
import subprocess
import time
import platform
from typing import Tuple, Optional
from urllib.parse import urlparse

import requests
import urllib3

# Disable SSL warnings for self-signed certificates and unverified HTTPS requests
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class ConnectionChecker:
    """Utility class for checking connection status."""
    
    def check_connection(self, connection) -> Tuple[str, Optional[float], Optional[str]]:
        """
        Check the status of a connection.
        
        Returns:
            Tuple of (status, response_time_ms, error_message)
            status: 'up', 'down', or 'unknown'
            response_time_ms: Response time in milliseconds (None if failed)
            error_message: Error message if connection failed (None if successful)
        """
        try:
            if connection.connection_type == 'http':
                return self._check_http(connection)
            elif connection.connection_type == 'ping':
                return self._check_ping(connection)
            elif connection.connection_type == 'tcp':
                return self._check_tcp(connection)
            elif connection.connection_type == 'database':
                return self._check_database(connection)
            else:
                return 'unknown', None, f'Unknown connection type: {connection.connection_type}'
        
        except Exception as e:
            return 'down', None, str(e)
    
    def _check_http(self, connection) -> Tuple[str, Optional[float], Optional[str]]:
        """Check HTTP/HTTPS connection."""
        try:
            start_time = time.time()
            
            # Prepare URL
            url = connection.target
            
            # Add port if specified and not already in URL
            if connection.port and f":{connection.port}" not in url:
                # Parse the URL to add port correctly
                if url.startswith(("http://", "https://")):
                    # URL already has protocol, add port before path
                    from urllib.parse import urlparse, urlunparse
                    parsed = urlparse(url)
                    if not parsed.port:  # Only add port if not already specified
                        netloc = f"{parsed.hostname}:{connection.port}"
                        if parsed.username:
                            netloc = f"{parsed.username}{":"+parsed.password if parsed.password else ""}@{netloc}"
                        url = urlunparse((parsed.scheme, netloc, parsed.path, parsed.params, parsed.query, parsed.fragment))
                else:
                    # No protocol, add port to hostname
                    url = f"{url}:{connection.port}"
            
            # Add protocol if missing
            if not url.startswith(("http://", "https://")):
                url = f"http://{url}"
            
            # Make request with proper headers for Cloudflare and other services
            headers = {
                'User-Agent': 'UpLite-Monitor/1.0 (Connection Monitor)',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache'
            }
            
            response = requests.get(
                url,
                timeout=connection.timeout,
                allow_redirects=True,
                verify=False,  # Don't verify SSL certificates
                headers=headers
            )
            
            end_time = time.time()
            response_time = (end_time - start_time) * 1000  # Convert to milliseconds
            
            # Check if response is successful OR authentication/authorization required
            # For protected services: 401=auth required, 403=forbidden but service is UP
            if response.status_code < 400 or response.status_code in [401, 403]:
                if response.status_code == 401:
                    return 'up', response_time, 'Service up (authentication required)'
                elif response.status_code == 403:
                    return 'up', response_time, 'Service up (access forbidden but responsive)'
                else:
                    return 'up', response_time, None
            else:
                return 'down', response_time, f'HTTP {response.status_code}: {response.reason}'
        
        except requests.exceptions.Timeout:
            return 'down', None, 'Connection timeout'
        except requests.exceptions.ConnectionError:
            return 'down', None, 'Connection refused'
        except requests.exceptions.RequestException as e:
            return 'down', None, str(e)
    
    def _check_ping(self, connection) -> Tuple[str, Optional[float], Optional[str]]:
        """Check ping connectivity."""
        try:
            # Determine ping command based on OS
            if platform.system().lower() == 'windows':
                cmd = ['ping', '-n', '1', '-w', str(connection.timeout * 1000), connection.target]
            else:
                cmd = ['ping', '-c', '1', '-W', str(connection.timeout), connection.target]
            
            start_time = time.time()
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=connection.timeout + 5)
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000
            
            if result.returncode == 0:
                # Try to extract actual ping time from output
                output = result.stdout.lower()
                if 'time=' in output:
                    try:
                        time_part = output.split('time=')[1].split()[0]
                        actual_ping_time = float(time_part.replace('ms', ''))
                        response_time = actual_ping_time
                    except (IndexError, ValueError):
                        pass
                
                return 'up', response_time, None
            else:
                return 'down', None, result.stderr.strip() or 'Ping failed'
        
        except subprocess.TimeoutExpired:
            return 'down', None, 'Ping timeout'
        except Exception as e:
            return 'down', None, str(e)
    
    def _check_tcp(self, connection) -> Tuple[str, Optional[float], Optional[str]]:
        """Check TCP connection."""
        try:
            start_time = time.time()
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(connection.timeout)
            
            result = sock.connect_ex((connection.target, connection.port or 80))
            
            end_time = time.time()
            response_time = (end_time - start_time) * 1000
            
            sock.close()
            
            if result == 0:
                return 'up', response_time, None
            else:
                return 'down', response_time, f'Connection failed (error code: {result})'
        
        except socket.timeout:
            return 'down', None, 'Connection timeout'
        except socket.gaierror as e:
            return 'down', None, f'DNS resolution failed: {e}'
        except Exception as e:
            return 'down', None, str(e)
    
    def _check_database(self, connection) -> Tuple[str, Optional[float], Optional[str]]:
        """Check database connection."""
        try:
            # This is a simplified database check
            # In a real implementation, you'd use database-specific drivers
            
            # For now, we'll treat it as a TCP check to the database port
            if not connection.port:
                # Set default ports for common databases
                if 'mysql' in connection.target.lower():
                    connection.port = 3306
                elif 'postgres' in connection.target.lower():
                    connection.port = 5432
                elif 'redis' in connection.target.lower():
                    connection.port = 6379
                elif 'mongodb' in connection.target.lower():
                    connection.port = 27017
                else:
                    connection.port = 3306  # Default to MySQL port
            
            return self._check_tcp(connection)
        
        except Exception as e:
            return 'down', None, str(e)
