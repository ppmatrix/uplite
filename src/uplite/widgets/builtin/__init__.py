"""Built-in widgets for UpLite."""

from .system_status import SystemStatusWidget
from .connection_monitor import ConnectionMonitorWidget
from .service_status import ServiceStatusWidget
from .logs_viewer import LogsViewerWidget

__all__ = [
    'SystemStatusWidget',
    'ConnectionMonitorWidget',
    'ServiceStatusWidget',
    'LogsViewerWidget'
]
