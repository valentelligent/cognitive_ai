"""
Development activity tracker for monitoring coding and development patterns
"""

import logging
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
import json
import os
from pathlib import Path
import psutil
import win32gui
import win32process
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from .interaction_tracker import InteractionTracker

class DevelopmentEventHandler(FileSystemEventHandler):
    def __init__(self, callback):
        self.callback = callback
        
    def on_modified(self, event):
        if not event.is_directory:
            self.callback('modified', event.src_path)
            
    def on_created(self, event):
        if not event.is_directory:
            self.callback('created', event.src_path)
            
    def on_deleted(self, event):
        if not event.is_directory:
            self.callback('deleted', event.src_path)
            
    def on_moved(self, event):
        if not event.is_directory:
            self.callback('moved', event.src_path, event.dest_path)

class DevelopmentTracker(InteractionTracker):
    def __init__(self, 
                 log_dir: str = "interaction_logs",
                 watched_paths: Optional[List[str]] = None):
        """Initialize development tracker"""
        try:
            super().__init__(log_dir)
            self.watched_paths = watched_paths or [os.getcwd()]
            self.observers = []
            self.dev_metrics = {
                # Code metrics
                "file_changes": [],  # Track file modifications
                "commit_patterns": [],  # Git commit frequency/size
                "code_complexity": [],  # Code complexity metrics
                
                # Development patterns
                "language_usage": {},  # Programming languages used
                "ide_patterns": [],  # IDE feature usage
                "debugging_sessions": [],  # Debugging patterns
                
                # Project metrics
                "project_structure": {},  # Project organization
                "dependency_changes": [],  # Package/dependency updates
                "build_events": []  # Build/compile events
            }
            
            # Set up file system observers
            self._setup_observers()
            
        except Exception as e:
            self.logger.error(f"Error initializing development tracker: {e}")
            raise
            
    def _setup_observers(self):
        """Set up file system observers for watched paths"""
        for path in self.watched_paths:
            try:
                observer = Observer()
                event_handler = DevelopmentEventHandler(self._handle_dev_event)
                observer.schedule(event_handler, path, recursive=True)
                self.observers.append(observer)
            except Exception as e:
                self.logger.error(f"Error setting up observer for {path}: {e}")
                
    def _handle_dev_event(self, event_type: str, src_path: str, dest_path: str = None):
        """Handle development events"""
        if not self.is_running:
            return
            
        event_data = {
            'type': 'development',
            'event_type': event_type,
            'src_path': src_path,
            'dest_path': dest_path,
            'timestamp': time.time(),
            'window_info': self._get_active_window_info()
        }
        
        self._log_event('development', event_data)
        
    def start(self):
        """Start the development tracker"""
        try:
            super().start()
            for observer in self.observers:
                observer.start()
        except Exception as e:
            self.logger.error(f"Error starting development tracker: {e}")
            self.stop()
            raise
            
    def stop(self):
        """Stop the development tracker"""
        try:
            for observer in self.observers:
                observer.stop()
                observer.join()
            super().stop()
        except Exception as e:
            self.logger.error(f"Error stopping development tracker: {e}")
            raise

if __name__ == '__main__':
    # Set up logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Test the development tracker
    tracker = DevelopmentTracker()
    try:
        tracker.start()
        time.sleep(60)  # Run for 1 minute
    finally:
        tracker.stop()
