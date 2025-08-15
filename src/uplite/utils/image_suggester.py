"""Image suggestion utility for UpLite connections."""

import os
import re
import shutil
import time
from difflib import SequenceMatcher
from typing import Optional, List, Dict, Tuple
from flask import current_app


class ImageSuggester:
    """Suggests images for connections based on name, description, and URL patterns."""
    
    def __init__(self, 
                 apps_icons_dir: str = "src/uplite/static/apps_icons",
                 connections_dir: str = "src/uplite/static/images/connections"):
        """Initialize the image suggester.
        
        Args:
            apps_icons_dir: Directory containing source app icons
            connections_dir: Directory where connection images are stored
        """
        self.apps_icons_dir = apps_icons_dir
        self.connections_dir = connections_dir
        self.available_icons = self._load_available_icons()
        
        # Service patterns for URL-based recognition
        self.service_patterns = {
            'proxmox': ['proxmox', 'pve'],
            'grafana': ['grafana'],
            'jenkins': ['jenkins'],
            'docker': ['docker', 'portainer'],
            'nginx': ['nginx'],
            'apache': ['apache', 'httpd'],
            'mysql': ['mysql', 'mariadb'],
            'postgresql': ['postgres', 'postgresql', 'pg'],
            'redis': ['redis'],
            'mongodb': ['mongo', 'mongodb'],
            'elasticsearch': ['elastic', 'elasticsearch'],
            'kibana': ['kibana'],
            'prometheus': ['prometheus'],
            'alertmanager': ['alertmanager'],
            'plex': ['plex'],
            'jellyfin': ['jellyfin'],
            'nextcloud': ['nextcloud'],
            'homeassistant': ['hass', 'homeassistant', 'home-assistant'],
            'pihole': ['pihole', 'pi-hole'],
            'adguard': ['adguard'],
            'sonarr': ['sonarr'],
            'radarr': ['radarr'],
            'lidarr': ['lidarr'],
            'bazarr': ['bazarr'],
            'transmission': ['transmission'],
            'deluge': ['deluge'],
            'qbittorrent': ['qbittorrent'],
            'portainer': ['portainer'],
            'watchtower': ['watchtower'],
            'traefik': ['traefik'],
            'caddy': ['caddy'],
            'minio': ['minio'],
            'gitea': ['gitea'],
            'gitlab': ['gitlab'],
            'github': ['github'],
            'bitwarden': ['bitwarden', 'vaultwarden'],
            'freshrss': ['freshrss'],
            'miniflux': ['miniflux'],
            'bookstack': ['bookstack'],
            'wikijs': ['wikijs', 'wiki'],
            'uptime': ['uptime', 'kuma'],
            'netdata': ['netdata'],
            'zabbix': ['zabbix'],
            'influxdb': ['influx'],
            'chronograf': ['chronograf'],
            'telegraf': ['telegraf']
        }
    
    def _load_available_icons(self) -> List[Dict[str, str]]:
        """Load all available app icons."""
        if not os.path.exists(self.apps_icons_dir):
            return []
        
        icons = []
        supported_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.svg'}
        
        try:
            for filename in os.listdir(self.apps_icons_dir):
                name, ext = os.path.splitext(filename)
                if ext.lower() in supported_extensions:
                    icons.append({
                        'filename': filename,
                        'name': name.lower(),
                        'keywords': self._extract_keywords(name),
                        'path': os.path.join(self.apps_icons_dir, filename)
                    })
        except OSError as e:
            current_app.logger.warning(f"Could not read apps_icons directory: {e}")
        
        return icons
    
    def _extract_keywords(self, filename: str) -> List[str]:
        """Extract searchable keywords from filename."""
        # Remove common suffixes and split on separators
        clean_name = re.sub(r'(logo|icon|app|service)$', '', filename.lower())
        keywords = re.split(r'[_\-\s\.]+', clean_name)
        return [k for k in keywords if len(k) > 1]  # Filter very short words
    
    def suggest_image(self, connection_name: str, 
                     connection_description: str = "", 
                     target_url: str = "",
                     connection_type: str = "") -> Optional[str]:
        """Suggest best matching image for a connection.
        
        Args:
            connection_name: Name of the connection
            connection_description: Description of the connection
            target_url: Target URL/IP of the connection
            connection_type: Type of connection (http, tcp, etc.)
            
        Returns:
            Filename of suggested icon or None if no good match found
        """
        if not self.available_icons:
            return None
        
        # Combine all text for searching
        search_text = f"{connection_name} {connection_description} {target_url}".lower()
        search_keywords = self._extract_keywords(search_text)
        
        best_match = None
        best_score = 0
        
        for icon in self.available_icons:
            score = self._calculate_match_score(
                icon, connection_name, search_keywords, target_url
            )
            
            if score > best_score:
                best_score = score
                best_match = icon['filename']
        
        # Return match only if score is above threshold
        return best_match if best_score >= 5 else None
    
    def _calculate_match_score(self, icon: Dict, connection_name: str, 
                              search_keywords: List[str], target_url: str) -> float:
        """Calculate match score for an icon."""
        score = 0.0
        icon_name = icon['name']
        icon_keywords = icon['keywords']
        
        # 1. Exact name match (highest priority)
        if connection_name.lower() == icon_name:
            score += 50
        
        # 2. Name similarity using sequence matcher
        name_similarity = SequenceMatcher(None, connection_name.lower(), icon_name).ratio()
        score += name_similarity * 20
        
        # 3. Service pattern recognition
        service_score = self._get_service_pattern_score(search_keywords + [connection_name.lower()], 
                                                       target_url, icon_name)
        score += service_score
        
        # 4. Keyword matching
        keyword_matches = 0
        for keyword in search_keywords:
            if keyword in icon_keywords or keyword in icon_name:
                keyword_matches += 1
            # Partial matches
            for icon_keyword in icon_keywords:
                if keyword in icon_keyword or icon_keyword in keyword:
                    keyword_matches += 0.5
        
        score += min(keyword_matches * 5, 15)  # Cap keyword score
        
        # 5. Substring matching
        for keyword in search_keywords:
            if len(keyword) > 3 and keyword in icon_name:
                score += 3
        
        return score
    
    def _get_service_pattern_score(self, search_terms: List[str], 
                                  target_url: str, icon_name: str) -> float:
        """Calculate score based on service pattern recognition."""
        url_lower = target_url.lower()
        combined_terms = ' '.join(search_terms + [url_lower])
        
        for service, patterns in self.service_patterns.items():
            # Check if any pattern matches in search terms or URL
            if any(pattern in combined_terms for pattern in patterns):
                # Check if icon name matches this service
                if service in icon_name or any(pattern in icon_name for pattern in patterns):
                    return 25  # High score for service pattern match
        
        return 0
    
    def copy_icon_to_connections(self, icon_filename: str) -> Optional[str]:
        """Copy an icon from apps_icons to connections directory.
        
        Args:
            icon_filename: Filename of the icon to copy
            
        Returns:
            New filename in connections directory or None if failed
        """
        if not icon_filename or icon_filename not in [i['filename'] for i in self.available_icons]:
            return None
        
        source_path = os.path.join(self.apps_icons_dir, icon_filename)
        if not os.path.exists(source_path):
            return None
        
        # Create destination directory if it doesn't exist
        os.makedirs(self.connections_dir, exist_ok=True)
        
        # Generate timestamped filename to avoid conflicts
        name, ext = os.path.splitext(icon_filename)
        timestamp = int(time.time())
        new_filename = f"{timestamp}_{icon_filename}"
        
        dest_path = os.path.join(self.connections_dir, new_filename)
        
        try:
            shutil.copy2(source_path, dest_path)
            return new_filename
        except OSError as e:
            current_app.logger.error(f"Failed to copy icon {icon_filename}: {e}")
            return None
    
    def get_available_icons(self) -> List[Dict[str, str]]:
        """Get list of all available icons with metadata."""
        return [{
            'filename': icon['filename'],
            'name': icon['name'],
            'keywords': icon['keywords']
        } for icon in self.available_icons]
    
    def search_icons(self, query: str, limit: int = 20) -> List[str]:
        """Search for icons matching a query.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of matching icon filenames
        """
        if not query or not self.available_icons:
            return []
        
        query_lower = query.lower()
        query_keywords = self._extract_keywords(query)
        
        matches = []
        for icon in self.available_icons:
            score = 0
            
            # Direct name match
            if query_lower in icon['name']:
                score += 10
            
            # Keyword matches
            for keyword in query_keywords:
                if keyword in icon['keywords'] or keyword in icon['name']:
                    score += 5
            
            if score > 0:
                matches.append((icon['filename'], score))
        
        # Sort by score and return top matches
        matches.sort(key=lambda x: x[1], reverse=True)
        return [filename for filename, score in matches[:limit]]

    def cleanup_unused_connection_images(self, used_filenames: List[str]) -> int:
        """Remove unused images from connections directory.
        
        Args:
            used_filenames: List of filenames currently in use
            
        Returns:
            Number of files cleaned up
        """
        if not os.path.exists(self.connections_dir):
            return 0
        
        cleaned_count = 0
        try:
            for filename in os.listdir(self.connections_dir):
                if filename not in used_filenames:
                    file_path = os.path.join(self.connections_dir, filename)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                        cleaned_count += 1
        except OSError as e:
            current_app.logger.error(f"Error during cleanup: {e}")
        
        return cleaned_count
