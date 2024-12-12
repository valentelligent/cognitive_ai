"""
Unit tests for the base interaction tracker
"""

import unittest
from unittest.mock import Mock, patch, mock_open
import json
from core.monitoring.interaction_tracker import InteractionTracker
import time
import psutil

class TestInteractionTracker(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.tracker = InteractionTracker(log_dir="test_logs")

    def tearDown(self):
        """Clean up after each test method."""
        if hasattr(self.tracker, 'is_running') and self.tracker.is_running:
            self.tracker.stop()

    def test_initialization(self):
        """Test tracker initialization."""
        self.assertFalse(self.tracker.is_running)
        self.assertIsNotNone(self.tracker.log_file)

    def test_start_stop(self):
        """Test starting and stopping the tracker."""
        self.tracker.start()
        self.assertTrue(self.tracker.is_running)
        
        self.tracker.stop()
        self.assertFalse(self.tracker.is_running)

    @patch('core.monitoring.interaction_tracker.keyboard')
    def test_keyboard_event_handling(self, mock_keyboard):
        """Test keyboard event handling."""
        self.tracker.start()
        
        # Create mock event
        event = Mock()
        event.name = 'a'
        event.event_type = 'down'
        
        # Test event handling
        with patch('builtins.open', mock_open()) as mock_file:
            self.tracker._handle_keyboard_event(event)
            mock_file().write.assert_called()

    @patch('core.monitoring.interaction_tracker.mouse')
    def test_mouse_event_handling(self, mock_mouse):
        """Test mouse event handling."""
        self.tracker.start()
        
        # Create mock event
        event = Mock()
        event.event_type = 'click'
        event.button = 'left'
        event.x = 100
        event.y = 100
        
        # Test event handling
        with patch('builtins.open', mock_open()) as mock_file:
            self.tracker._handle_mouse_event(event)
            mock_file().write.assert_called()

    @patch('core.monitoring.interaction_tracker.win32gui')
    def test_window_tracking(self, mock_win32gui):
        """Test active window tracking."""
        mock_win32gui.GetWindowText.return_value = "Test Window"
        mock_win32gui.GetForegroundWindow.return_value = 12345
        
        window_info = self.tracker._get_active_window()
        self.assertEqual(window_info['window_title'], "Test Window")
        self.assertEqual(window_info['window_handle'], 12345)

    def test_log_event(self):
        """Test event logging functionality."""
        self.tracker.start()
        
        test_event = {
            'key': 'a',
            'event_type': 'down',
            'time': time.time()
        }
        
        with patch('builtins.open', mock_open()) as mock_file:
            self.tracker._log_event('test', test_event)
            mock_file().write.assert_called_once()
            
            # Get the JSON string that was written (remove trailing newline)
            json_str = mock_file().write.call_args[0][0].rstrip('\n')
            
            # Parse and verify the event data
            event_data = json.loads(json_str)
            self.assertEqual(event_data['type'], 'test')
            self.assertIn('timestamp', event_data)
            self.assertIn('window', event_data)
            self.assertIn('system_metrics', event_data)
            self.assertEqual(event_data['key'], 'a')
            self.assertEqual(event_data['event_type'], 'down')
        
        self.tracker.stop()

    @patch('core.monitoring.interaction_tracker.psutil')
    def test_system_metrics(self, mock_psutil):
        """Test system resource monitoring."""
        mock_psutil.cpu_percent.return_value = 50.0
        mock_psutil.virtual_memory.return_value = Mock(percent=75.0)
        
        metrics = self.tracker._get_system_metrics()
        self.assertIn('cpu_usage', metrics)
        self.assertIn('memory_usage', metrics)
        self.assertEqual(metrics['cpu_usage'], 50.0)
        self.assertEqual(metrics['memory_usage'], 75.0)

    def test_system_metrics(self):
        """Test system resource monitoring."""
        metrics = self.tracker._get_system_metrics()
        self.assertIn('cpu_usage', metrics)
        self.assertIn('memory_usage', metrics)
        self.assertIsInstance(metrics['cpu_usage'], float)
        self.assertIsInstance(metrics['memory_usage'], float)
        self.assertTrue(0 <= metrics['cpu_usage'] <= 100)
        self.assertTrue(0 <= metrics['memory_usage'] <= 100)

    def test_window_tracking(self):
        """Test active window tracking."""
        window_info = self.tracker._get_active_window_info()
        self.assertIn('window_title', window_info)
        self.assertIn('application', window_info)
        self.assertIn('pid', window_info)

    def test_latency_measurement(self):
        """Test event processing latency."""
        self.tracker.start()
        start_time = time.time()
        
        # Simulate keyboard event
        event = Mock()
        event.name = 'a'
        event.event_type = 'down'
        
        with patch('builtins.open', mock_open()) as mock_file:
            self.tracker._handle_keyboard_event(event)
            processing_time = time.time() - start_time
            self.assertLess(processing_time, 0.1)  # Event processing should take less than 100ms

    def test_high_frequency_events(self):
        """Test handling of rapid event sequences."""
        self.tracker.start()
        events_processed = 0
        max_events = 1000
        start_time = time.time()

        # Simulate rapid keyboard events
        event = Mock()
        event.name = 'a'
        event.event_type = 'down'
        
        with patch('builtins.open', mock_open()):
            for _ in range(max_events):
                self.tracker._handle_keyboard_event(event)
                events_processed += 1
        
        processing_time = time.time() - start_time
        events_per_second = events_processed / processing_time
        
        self.assertGreater(events_per_second, 100)  # Should handle at least 100 events per second

    def test_error_recovery(self):
        """Test system recovery from simulated errors."""
        self.tracker.start()
        initial_events_count = len(self.tracker.events)
        
        # Simulate file system error
        with patch('builtins.open', side_effect=IOError("Simulated IO Error")):
            event = Mock()
            event.name = 'a'
            event.event_type = 'down'
            
            # Should not raise exception and should store event in memory
            self.tracker._handle_keyboard_event(event)
            self.assertTrue(self.tracker.is_running)
            self.assertEqual(len(self.tracker.events), initial_events_count + 1)

        # System should continue working after error
        with patch('builtins.open', mock_open()) as mock_file:
            event = Mock()
            event.name = 'b'
            event.event_type = 'down'
            self.tracker._handle_keyboard_event(event)
            mock_file().write.assert_called()
            self.assertEqual(len(self.tracker.events), initial_events_count + 2)

        # Test error recovery during event flush
        with patch('builtins.open', side_effect=IOError("Simulated Flush Error")):
            self.tracker._flush_events()
            # Events should be preserved in memory
            self.assertGreater(len(self.tracker.events), 0)

    def test_resource_cleanup(self):
        """Test proper resource cleanup on shutdown."""
        self.tracker.start()
        initial_process_count = len(psutil.Process().children())
        
        # Create some events
        event = Mock()
        event.name = 'a'
        event.event_type = 'down'
        with patch('builtins.open', mock_open()):
            for _ in range(10):
                self.tracker._handle_keyboard_event(event)
        
        self.tracker.stop()
        time.sleep(0.1)  # Allow time for cleanup
        
        final_process_count = len(psutil.Process().children())
        self.assertEqual(initial_process_count, final_process_count)
        self.assertFalse(self.tracker.is_running)

if __name__ == '__main__':
    unittest.main()
