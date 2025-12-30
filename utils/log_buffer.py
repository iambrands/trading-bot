"""In-memory log buffer for capturing logs for the web UI."""

import logging
from datetime import datetime
from collections import deque
from typing import List, Dict, Optional


class InMemoryLogHandler(logging.Handler):
    """Custom logging handler that stores logs in memory."""
    
    def __init__(self, max_size: int = 1000):
        """
        Initialize the in-memory log handler.
        
        Args:
            max_size: Maximum number of log entries to keep in memory (default: 1000)
        """
        super().__init__()
        self.logs = deque(maxlen=max_size)  # Use deque with maxlen for automatic rotation
        self.max_size = max_size
    
    def emit(self, record: logging.LogRecord):
        """Emit a log record to the in-memory buffer."""
        try:
            # Format the log message
            message = self.format(record)
            
            # Parse the formatted message to extract components
            # Format: "2025-11-25 22:01:23,330 - module - LEVEL - message"
            parts = message.split(' - ', 3)
            
            if len(parts) >= 4:
                timestamp_str = parts[0]
                module = parts[1]
                level = parts[2]
                log_message = parts[3]
            else:
                # Fallback if format doesn't match
                timestamp_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S,%f')[:-3]
                module = record.name
                level = record.levelname
                log_message = record.getMessage()
            
            # Convert timestamp to ISO format
            timestamp_iso = timestamp_str
            try:
                if ',' in timestamp_str:
                    dt_str, ms_str = timestamp_str.split(',', 1)
                    dt_obj = datetime.strptime(dt_str.strip(), '%Y-%m-%d %H:%M:%S')
                    ms = ms_str.strip()[:3].ljust(3, '0')
                    timestamp_iso = dt_obj.isoformat() + '.' + ms + 'Z'
                else:
                    dt_obj = datetime.strptime(timestamp_str.strip(), '%Y-%m-%d %H:%M:%S')
                    timestamp_iso = dt_obj.isoformat() + '.000Z'
            except Exception:
                # Fallback: use current time
                timestamp_iso = datetime.now().isoformat() + 'Z'
            
            # Store the log entry
            log_entry = {
                'timestamp': timestamp_iso,
                'timestamp_raw': timestamp_str,
                'module': module,
                'level': level,
                'message': log_message
            }
            
            self.logs.append(log_entry)
        except Exception:
            # Ignore errors in logging handler to prevent infinite loops
            pass
    
    def get_logs(self, limit: Optional[int] = None, level_filter: Optional[str] = None) -> List[Dict]:
        """
        Get logs from the buffer.
        
        Args:
            limit: Maximum number of logs to return (None = all)
            level_filter: Filter by log level (None = all levels)
        
        Returns:
            List of log dictionaries
        """
        logs = list(self.logs)
        
        # Apply level filter
        if level_filter and level_filter != 'ALL':
            logs = [log for log in logs if log['level'] == level_filter]
        
        # Apply limit (return most recent logs)
        if limit:
            logs = logs[-limit:]
        
        return logs
    
    def clear(self):
        """Clear all logs from the buffer."""
        self.logs.clear()


# Global instance
_log_handler: Optional[InMemoryLogHandler] = None


def get_log_handler(max_size: int = 1000) -> InMemoryLogHandler:
    """Get or create the global log handler instance."""
    global _log_handler
    if _log_handler is None:
        _log_handler = InMemoryLogHandler(max_size=max_size)
    return _log_handler


def setup_log_buffer(max_size: int = 1000) -> InMemoryLogHandler:
    """
    Setup the in-memory log buffer and add it to the root logger.
    
    Args:
        max_size: Maximum number of log entries to keep
    
    Returns:
        The log handler instance
    """
    handler = get_log_handler(max_size=max_size)
    
    # Add to root logger if not already added
    root_logger = logging.getLogger()
    if handler not in root_logger.handlers:
        root_logger.addHandler(handler)
    
    return handler

