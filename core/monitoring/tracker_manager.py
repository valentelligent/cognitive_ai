import logging
import time
from pathlib import Path
from datetime import datetime
import threading
import queue


class BaseTracker(threading.Thread):
    def __init__(self, name: str, log_dir: Path):
        super().__init__(daemon=True)
        self.name = name
        self.log_dir = log_dir
        self.running = False
        self.queue = queue.Queue()

        # Setup logger
        self.logger = logging.getLogger(f"tracker.{name}")
        self.setup_logger()

    def setup_logger(self):
        """Setup a dedicated file handler for this tracker"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = self.log_dir / f"{self.name}_{timestamp}.log"
        handler = logging.FileHandler(log_file)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def run(self):
        try:
            self.running = True
            self.logger.info(f"{self.name} tracker started")

            while self.running:
                try:
                    try:
                        event = self.queue.get(timeout=1.0)
                        self.process_event(event)
                        if self.queue.qsize() % 10 == 0:
                            self.logger.debug("Heartbeat")
                    except queue.Empty:
                        self.logger.debug("Idle heartbeat")
                        time.sleep(1)
                except Exception as e:
                    self.logger.error(f"Error processing event in {self.name} tracker: {e}")
                    time.sleep(1)
        except Exception as e:
            self.logger.error(f"Fatal error in {self.name} tracker: {e}")
            self.running = False
        finally:
            self.logger.info(f"{self.name} tracker stopped")

    def process_event(self, event):
        """Process a single event. Override in subclasses."""
        self.logger.debug(f"Processing event: {event}")

    def stop(self):
        """Gracefully stop the tracker."""
        self.logger.info(f"Stopping {self.name} tracker...")
        self.running = False
        self.join(timeout=5.0)
        self.logger.info(f"{self.name} tracker stopped")


class CognitiveTracker(BaseTracker):
    def process_event(self, event):
        """Process cognitive events like code understanding and generation."""
        try:
            if isinstance(event, dict):
                event_type = event.get('type', 'unknown')
                self.logger.info(f"Processing cognitive event: {event_type}")

                if event_type == 'code_generation':
                    code_len = len(event.get('code', ''))
                    self.logger.info(f"Code generated: {code_len} characters")
                elif event_type == 'code_analysis':
                    self.logger.info(f"Analyzed file: {event.get('file', 'unknown')}")
                elif event_type == 'error_analysis':
                    self.logger.info(f"Analyzed error: {event.get('error', 'unknown')}")

                self.logger.debug(f"Event details: {event}")
        except Exception as e:
            self.logger.error(f"Error processing cognitive event: {e}")


class InteractionTracker(BaseTracker):
    def __init__(self, name: str, log_dir: Path):
        super().__init__(name, log_dir)
        self.last_activity = datetime.now()
        self.activity_count = 0

    def process_event(self, event):
        """Process user interaction events."""
        try:
            if isinstance(event, dict):
                event_type = event.get('type', 'unknown')
                self.logger.info(f"Processing interaction event: {event_type}")

                self.last_activity = datetime.now()
                self.activity_count += 1

                if event_type == 'keypress':
                    self.logger.info(f"Key pressed: {event.get('key', 'unknown')}")
                elif event_type == 'mouse':
                    self.logger.info(f"Mouse action: {event.get('action', 'unknown')}")
                elif event_type == 'command':
                    self.logger.info(f"Command executed: {event.get('command', 'unknown')}")

                if self.activity_count % 100 == 0:
                    self.log_session_metrics()
        except Exception as e:
            self.logger.error(f"Error processing interaction event: {e}")

    def log_session_metrics(self):
        """Log session activity metrics"""
        try:
            duration = datetime.now() - self.last_activity
            metrics = (f"Session metrics - Events: {self.activity_count}, "
                      f"Last activity: {duration.total_seconds():.1f}s ago")
            self.logger.info(metrics)
        except Exception as e:
            self.logger.error(f"Error logging session metrics: {e}")


class DevelopmentTracker(BaseTracker):
    def __init__(self, name: str, log_dir: Path):
        super().__init__(name, log_dir)
        self.file_changes = {}
        self.last_commit = None

    def process_event(self, event):
        """Process development events like file changes and builds."""
        try:
            if isinstance(event, dict):
                event_type = event.get('type', 'unknown')
                self.logger.info(f"Processing development event: {event_type}")

                if event_type == 'file_change':
                    self.track_file_change(event)
                elif event_type == 'git':
                    self.track_git_event(event)
                elif event_type == 'build':
                    self.track_build_event(event)

                should_log = (self.last_commit is None or
                            (datetime.now() - self.last_commit).total_seconds() > 3600)
                if should_log:
                    self.log_development_metrics()
        except Exception as e:
            self.logger.error(f"Error processing development event: {e}")

    def track_file_change(self, event):
        """Track file modifications"""
        try:
            file_path = event.get('file', 'unknown')
            change_type = event.get('change_type', 'unknown')

            if file_path not in self.file_changes:
                self.file_changes[file_path] = {
                    'modifications': 0,
                    'last_modified': None
                }

            self.file_changes[file_path]['modifications'] += 1
            self.file_changes[file_path]['last_modified'] = datetime.now()

            self.logger.info(f"File {change_type}: {file_path} "
                           f"(Total modifications: {self.file_changes[file_path]['modifications']})")
        except Exception as e:
            self.logger.error(f"Error tracking file change: {e}")

    def track_git_event(self, event):
        """Track git operations"""
        try:
            operation = event.get('operation', 'unknown')
            self.last_commit = datetime.now()
            self.logger.info(f"Git operation: {operation}")
        except Exception as e:
            self.logger.error(f"Error tracking git event: {e}")

    def track_build_event(self, event):
        """Track build events"""
        try:
            status = event.get('status', 'unknown')
            duration = event.get('duration', 0)
            self.logger.info(f"Build {status} (Duration: {duration:.1f}s)")
        except Exception as e:
            self.logger.error(f"Error tracking build event: {e}")

    def log_development_metrics(self):
        """Log development activity metrics"""
        try:
            total_files = len(self.file_changes)
            total_modifications = sum(f['modifications'] for f in self.file_changes.values())

            self.logger.info(f"Development metrics - Files modified: {total_files}, "
                           f"Total modifications: {total_modifications}")

            # Reset metrics after logging
            self.file_changes = {}
        except Exception as e:
            self.logger.error(f"Error logging development metrics: {e}")


class TrackerManager:
    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.log_dir = self.project_root / 'logs'
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Setup manager logger
        self.logger = logging.getLogger(__name__)
        self.setup_logger()

        # Initialize trackers
        self.trackers = {}
        self.initialize_trackers()

    def setup_logger(self):
        """Setup the manager's logger"""
        log_file = self.log_dir / "tracker_manager.log"
        handler = logging.FileHandler(log_file)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def initialize_trackers(self):
        """Initialize all tracker instances"""
        try:
            self.trackers['cognitive'] = CognitiveTracker('cognitive', self.log_dir)
            self.trackers['interaction'] = InteractionTracker('interaction', self.log_dir)
            self.trackers['development'] = DevelopmentTracker('development', self.log_dir)
            self.logger.info("All trackers initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize trackers: {e}")
            raise

    def start_all_trackers(self) -> bool:
        """Start all tracker threads"""
        try:
            for name, tracker in self.trackers.items():
                self.logger.info(f"Starting {name} tracker...")
                tracker.start()
                # Wait a bit to ensure the tracker starts properly
                time.sleep(0.5)
                if not tracker.is_alive():
                    self.logger.error(f"{name} tracker failed to start")
                    return False
            self.logger.info("All trackers started successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to start trackers: {e}")
            return False

    def check_tracker_status(self) -> dict:
        """Check the status of all trackers"""
        status = {}
        for name, tracker in self.trackers.items():
            try:
                if tracker.is_alive():
                    status[name] = 'running'
                else:
                    status[name] = 'stopped'
            except Exception as e:
                self.logger.error(f"Error checking {name} tracker status: {e}")
                status[name] = 'error'
        return status

    def stop_all_trackers(self) -> bool:
        """Gracefully stop all trackers"""
        try:
            for name, tracker in self.trackers.items():
                self.logger.info(f"Stopping {name} tracker...")
                tracker.stop()
            self.logger.info("All trackers stopped successfully")
            return True
        except Exception as e:
            self.logger.error(f"Error stopping trackers: {e}")
            return False
