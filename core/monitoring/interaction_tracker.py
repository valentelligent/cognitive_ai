"""
Comprehensive interaction tracking system for capturing and analyzing user behavior patterns.
"""

import logging
import time
from datetime import datetime
from typing import Dict, Any, List
import json
import os
from pathlib import Path
import keyboard
import mouse
import psutil
import win32gui
import win32process
import threading

class InteractionTracker:
    def __init__(self, log_dir: str = "interaction_logs"):
        self.logger = logging.getLogger(__name__)
        self.log_dir = Path(log_dir)
        self.is_running = False
        self.log_file = None
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self._setup_log_file()
        self.current_session = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.events: List[Dict] = []
        self.last_event_time = time.time()
        
        # Initialize event handlers
        self._setup_keyboard_hooks()
        self._setup_mouse_hooks()
        
    def _setup_log_file(self):
        """Set up the log file with current timestamp"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = os.path.join(self.log_dir, f"interaction_log_{timestamp}.jsonl")

    def _setup_keyboard_hooks(self):
        """Set up keyboard event hooks"""
        keyboard.hook(self._handle_keyboard_event)
        
    def _setup_mouse_hooks(self):
        """Set up mouse event hooks"""
        mouse.hook(self._handle_mouse_event)
        
    def _get_active_window_info(self) -> Dict[str, str]:
        """Get information about the currently active window."""
        try:
            window = win32gui.GetForegroundWindow()
            _, pid = win32process.GetWindowThreadProcessId(window)
            process = psutil.Process(pid)
            return {
                'window_title': win32gui.GetWindowText(window),
                'application': process.name(),
                'pid': pid
            }
        except Exception as e:
            self.logger.error(f"Error getting window info: {e}")
            return {'window_title': 'unknown', 'application': 'unknown', 'pid': 0}
            
    def _get_system_metrics(self) -> Dict:
        """Get current system resource usage"""
        return {
            'cpu_usage': psutil.cpu_percent(),
            'memory_usage': psutil.virtual_memory().percent
        }
        
    def _handle_keyboard_event(self, event):
        """Handle keyboard events."""
        if not self.is_running:
            return

        event_data = {
            'type': 'keyboard',
            'key': event.name,
            'event_type': event.event_type,
            'timestamp': time.time()
        }
        self._log_event('keyboard', event_data)
        
    def _handle_mouse_event(self, event):
        """Handle mouse events"""
        if not self.is_running:
            return

        event_data = {
            'type': 'mouse',
            'event_type': event.event_type,
            'position': (event.x, event.y) if hasattr(event, 'x') else None,
            'button': event.button if hasattr(event, 'button') else None,
            'timestamp': time.time()
        }
        self._log_event('mouse', event_data)
            
    def _get_active_window(self) -> Dict:
        """Get information about the currently active window"""
        window_handle = win32gui.GetForegroundWindow()
        window_title = win32gui.GetWindowText(window_handle)
        return {
            'window_handle': window_handle,
            'window_title': window_title
        }

    def _log_event(self, event_type: str, context: Dict):
        """Log an interaction event with context"""
        if not self.is_running:
            return

        try:
            event_data = {
                'timestamp': time.time(),
                'type': event_type,
                'window': self._get_active_window(),
                'system_metrics': self._get_system_metrics(),
                **context
            }

            json_str = json.dumps(event_data)
            try:
                with open(self.log_file, 'a', encoding='utf-8') as f:
                    f.write(json_str + '\n')
            except (IOError, OSError) as e:
                self.logger.error(f"Failed to write to log file: {e}")
                # Store event in memory if file write fails
                self.events.append(event_data)
                return
            
            self.events.append(event_data)
            self.last_event_time = time.time()
            
            # Write to file periodically
            if len(self.events) >= 100:
                self._flush_events()
        except Exception as e:
            self.logger.error(f"Error in _log_event: {e}")
            # Ensure we don't lose the event even if processing fails
            if context:
                self.events.append({
                    'timestamp': time.time(),
                    'type': event_type,
                    'error': str(e),
                    **context
                })
        
    def _flush_events(self):
        """Write accumulated events to disk."""
        if not self.events:
            return
            
        try:
            log_file = self.log_dir / f"interaction_log_{self.current_session}.jsonl"
            events_to_write = self.events.copy()  # Copy events to prevent data loss
            
            try:
                with open(log_file, 'a', encoding='utf-8') as f:
                    for event in events_to_write:
                        f.write(json.dumps(event) + '\n')
                self.events.clear()  # Only clear if write was successful
            except (IOError, OSError) as e:
                self.logger.error(f"Failed to flush events: {e}")
                # Keep events in memory if flush fails
                return
        except Exception as e:
            self.logger.error(f"Error in _flush_events: {e}")
        
    def start(self):
        """Start tracking interactions with enhanced error handling."""
        if self.is_running:
            self.logger.warning("Tracker is already running")
            return

        try:
            self.is_running = True
            self.logger.info(f"Starting interaction tracker. Logging to: {self.log_file}")
            
            # Setup error recovery
            self._last_flush_time = time.time()
            self._error_count = 0
            self._max_errors = 3
            
            # Start monitoring thread
            self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self._monitor_thread.start()
            
        except Exception as e:
            self.logger.error(f"Error starting tracker: {e}")
            self.is_running = False
            raise

    def _monitor_loop(self):
        """Monitor the tracking system and handle errors"""
        while self.is_running:
            try:
                # Flush events periodically
                current_time = time.time()
                if current_time - self._last_flush_time > 30:  # Flush every 30 seconds
                    self._flush_events()
                    self._last_flush_time = current_time
                
                # Reset error count after successful operation
                self._error_count = 0
                
                time.sleep(1)
                
            except Exception as e:
                self._error_count += 1
                self.logger.error(f"Error in monitor loop: {e}")
                
                if self._error_count >= self._max_errors:
                    self.logger.critical("Too many errors, stopping tracker")
                    self.stop()
                    break
                    
                time.sleep(5)  # Wait before retry

    def stop(self):
        """Stop tracking interactions and clean up."""
        if self.is_running:
            self.is_running = False
            self.logger.info("Stopping interaction tracking...")
            keyboard.unhook_all()
            mouse.unhook_all()
            self._flush_events()  # Ensure all remaining events are written
        
    def get_current_stats(self) -> Dict[str, Any]:
        """Get current tracking statistics."""
        return {
            'total_events': len(self.events),
            'session_duration': time.time() - self.last_event_time,
            'current_window': self._get_active_window_info(),
            'system_metrics': self._get_system_metrics()
        }

if __name__ == '__main__':
    # Set up logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('interaction_tracker_debug.log')
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info("Starting interaction tracker...")
    
    try:
        tracker = InteractionTracker()
        logger.info(f"Tracker initialized. Log file: {tracker.log_file}")
        tracker.start()
        logger.info("Tracker started successfully")
        
        # Keep the main thread alive
        while True:
            time.sleep(1)
            
    except Exception as e:
        logger.error(f"Error in main loop: {e}", exc_info=True)
        raise
