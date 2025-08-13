"""Base widget class for UpLite dashboard widgets."""

from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseWidget(ABC):
    """Base class for all dashboard widgets."""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the widget with configuration."""
        self.config = config or {}
    
    @property
    @abstractmethod
    def widget_type(self) -> str:
        """Return the widget type identifier."""
        pass
    
    @property
    @abstractmethod
    def display_name(self) -> str:
        """Return the display name of the widget."""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Return the description of the widget."""
        pass
    
    @abstractmethod
    def get_data(self) -> Dict[str, Any]:
        """Get the widget data to be displayed."""
        pass
    
    @property
    def default_config(self) -> Dict[str, Any]:
        """Return the default configuration for this widget."""
        return {}
    
    @property
    def config_schema(self) -> Dict[str, Any]:
        """Return the configuration schema for this widget."""
        return {}
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate the widget configuration."""
        # Basic validation can be implemented here
        # Override in subclasses for specific validation
        return True
    
    def get_template_name(self) -> str:
        """Get the template name for rendering this widget."""
        return f'widgets/{self.widget_type}.html'
    
    def get_css_classes(self) -> str:
        """Get CSS classes for the widget container."""
        return f'widget widget-{self.widget_type}'
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert widget to dictionary representation."""
        return {
            'type': self.widget_type,
            'display_name': self.display_name,
            'description': self.description,
            'config': self.config,
            'default_config': self.default_config,
            'config_schema': self.config_schema
        }
