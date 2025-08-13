"""Widget manager for handling dashboard widgets."""

import importlib
import os
from typing import Dict, Any, List, Type

from .base_widget import BaseWidget


class WidgetManager:
    """Manager for dashboard widgets."""
    
    _widgets: Dict[str, Type[BaseWidget]] = {}
    _initialized = False
    
    @classmethod
    def initialize(cls):
        """Initialize the widget manager by loading all available widgets."""
        if cls._initialized:
            return
        
        cls._load_builtin_widgets()
        cls._initialized = True
    
    @classmethod
    def _load_builtin_widgets(cls):
        """Load built-in widgets."""
        from .builtin.system_status import SystemStatusWidget
        from .builtin.connection_monitor import ConnectionMonitorWidget
        from .builtin.service_status import ServiceStatusWidget
        from .builtin.logs_viewer import LogsViewerWidget
        
        widgets = [
            SystemStatusWidget,
            ConnectionMonitorWidget,
            ServiceStatusWidget,
            LogsViewerWidget
        ]
        
        for widget_class in widgets:
            cls.register_widget(widget_class)
    
    @classmethod
    def register_widget(cls, widget_class: Type[BaseWidget]):
        """Register a widget class."""
        if not issubclass(widget_class, BaseWidget):
            raise ValueError(f"{widget_class} must inherit from BaseWidget")
        
        # Create an instance to get the widget type
        instance = widget_class()
        cls._widgets[instance.widget_type] = widget_class
    
    @classmethod
    def get_widget(cls, widget_type: str, config: Dict[str, Any] = None) -> BaseWidget:
        """Get a widget instance by type."""
        cls.initialize()
        
        if widget_type not in cls._widgets:
            raise ValueError(f"Unknown widget type: {widget_type}")
        
        widget_class = cls._widgets[widget_type]
        return widget_class(config)
    
    @classmethod
    def get_available_widgets(cls) -> List[Dict[str, Any]]:
        """Get list of available widgets with their metadata."""
        cls.initialize()
        
        widgets = []
        for widget_type, widget_class in cls._widgets.items():
            instance = widget_class()
            widgets.append(instance.to_dict())
        
        return widgets
    
    @classmethod
    def get_widget_data(cls, widget_type: str, config: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get data for a specific widget."""
        widget = cls.get_widget(widget_type, config)
        return widget.get_data()
    
    @classmethod
    def validate_widget_config(cls, widget_type: str, config: Dict[str, Any]) -> bool:
        """Validate configuration for a widget type."""
        cls.initialize()
        
        if widget_type not in cls._widgets:
            return False
        
        widget_class = cls._widgets[widget_type]
        instance = widget_class()
        return instance.validate_config(config)
