// UpLite Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Connection status checker
    if (typeof checkConnections === 'function') {
        // Initial check
        checkConnections();
        
        // Periodic checks every 5 minutes
        setInterval(checkConnections, 300000);
    }
});

// Global functions
window.UpLite = {
    // API helper functions
    api: {
        get: function(url) {
            return fetch(url, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
            }).then(response => response.json());
        },
        
        post: function(url, data) {
            return fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            }).then(response => response.json());
        },
        
        put: function(url, data) {
            return fetch(url, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            }).then(response => response.json());
        }
    },

    // Utility functions
    utils: {
        formatBytes: function(bytes, decimals = 2) {
            if (bytes === 0) return '0 Bytes';
            
            const k = 1024;
            const dm = decimals < 0 ? 0 : decimals;
            const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
            
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            
            return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
        },
        
        formatDuration: function(seconds) {
            const hours = Math.floor(seconds / 3600);
            const minutes = Math.floor((seconds % 3600) / 60);
            const secs = Math.floor(seconds % 60);
            
            if (hours > 0) {
                return `${hours}h ${minutes}m ${secs}s`;
            } else if (minutes > 0) {
                return `${minutes}m ${secs}s`;
            } else {
                return `${secs}s`;
            }
        },
        
        debounce: function(func, wait, immediate) {
            let timeout;
            return function() {
                const context = this, args = arguments;
                const later = function() {
                    timeout = null;
                    if (!immediate) func.apply(context, args);
                };
                const callNow = immediate && !timeout;
                clearTimeout(timeout);
                timeout = setTimeout(later, wait);
                if (callNow) func.apply(context, args);
            };
        }
    },

    // Notification system
    notify: {
        show: function(message, type = 'info', duration = 5000) {
            const alertDiv = document.createElement('div');
            alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
            alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 1050; min-width: 300px;';
            alertDiv.innerHTML = `
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            `;
            
            document.body.appendChild(alertDiv);
            
            // Auto-remove after duration
            setTimeout(function() {
                const bsAlert = new bootstrap.Alert(alertDiv);
                bsAlert.close();
            }, duration);
        },
        
        success: function(message) {
            this.show(message, 'success');
        },
        
        error: function(message) {
            this.show(message, 'danger', 8000);
        },
        
        warning: function(message) {
            this.show(message, 'warning');
        },
        
        info: function(message) {
            this.show(message, 'info');
        }
    }
};

// Connection status functions
function checkConnections() {
    UpLite.api.get('/api/dashboard/refresh')
        .then(function(data) {
            console.log('Dashboard refreshed:', data);
            // Update UI if needed
        })
        .catch(function(error) {
            console.error('Error refreshing dashboard:', error);
        });
}

// Widget management functions
function refreshWidget(widgetId) {
    const widgetElement = document.getElementById(`widget-${widgetId}`);
    if (!widgetElement) return;
    
    // Show loading state
    const widgetBody = widgetElement.querySelector('.widget-body');
    const originalContent = widgetBody.innerHTML;
    widgetBody.innerHTML = `
        <div class="text-center">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <p class="mt-2">Refreshing...</p>
        </div>
    `;
    
    // Load widget data
    UpLite.api.get(`/api/widgets/${widgetId}/data`)
        .then(function(data) {
            if (data.error) {
                widgetBody.innerHTML = `<div class="alert alert-danger">${data.error}</div>`;
            } else {
                // Render widget data (implementation would depend on widget type)
                renderWidgetData(widgetId, data, widgetBody);
            }
        })
        .catch(function(error) {
            widgetBody.innerHTML = originalContent;
            UpLite.notify.error('Failed to refresh widget');
        });
}

function renderWidgetData(widgetId, data, widgetBody) {
    // This would be implemented based on widget types
    // For now, just show raw data
    widgetBody.innerHTML = `<pre>${JSON.stringify(data, null, 2)}</pre>`;
}
