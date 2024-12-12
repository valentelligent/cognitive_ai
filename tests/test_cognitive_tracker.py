"""
Unit tests for the cognitive interaction tracker
"""

import unittest
from unittest.mock import Mock, patch
from datetime import datetime, time
from core.monitoring.interaction_tracker import InteractionTracker
from core.monitoring.cognitive_tracker import CognitiveInteractionTracker

class TestCognitiveInteractionTracker(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.schedule = {
            "coding": [time(9, 0), time(12, 0)],
            "reading": [time(13, 0), time(15, 0)]
        }
        self.tracker = CognitiveInteractionTracker(schedule=self.schedule)

    def tearDown(self):
        """Clean up after each test method."""
        if hasattr(self.tracker, 'is_running') and self.tracker.is_running:
            self.tracker.stop()

    def test_initialization(self):
        """Test tracker initialization."""
        self.assertEqual(self.tracker.schedule, self.schedule)
        self.assertIsNone(self.tracker.current_task)
        self.assertIn("coding", self.tracker.task_types)
        self.assertIn("reading", self.tracker.task_types)

    def test_start_stop_task(self):
        """Test starting and stopping tasks."""
        self.tracker.start_task("coding")
        self.assertEqual(self.tracker.current_task, "coding")
        
        self.tracker.stop_task()
        self.assertIsNone(self.tracker.current_task)

    def test_invalid_task_type(self):
        """Test handling of invalid task types."""
        with self.assertRaises(ValueError):
            self.tracker.start_task("invalid_task")

    @patch('core.monitoring.interaction_tracker.datetime')
    def test_task_schedule_validation(self, mock_datetime):
        """Test task schedule validation."""
        # Mock current time to 10:00 AM
        mock_time = Mock()
        mock_time.hour = 10
        mock_time.minute = 0
        mock_datetime.now.return_value = Mock(time=lambda: mock_time)

        self.tracker.start_task("coding")
        self.assertEqual(self.tracker.current_task, "coding")

    @patch('core.monitoring.interaction_tracker.keyboard')
    @patch('core.monitoring.interaction_tracker.mouse')
    def test_interaction_tracking(self, mock_mouse, mock_keyboard):
        """Test keyboard and mouse interaction tracking."""
        self.tracker.start()
        
        # Simulate keyboard event
        keyboard_event = Mock()
        keyboard_event.name = 'a'
        keyboard_event.event_type = 'down'
        keyboard_event.time = datetime.now().timestamp()
        self.tracker._handle_keyboard_event(keyboard_event)
        
        # Simulate mouse event
        mouse_event = Mock()
        mouse_event.event_type = 'click'
        mouse_event.button = 'left'
        mouse_event.x = 100
        mouse_event.y = 100
        mouse_event.time = datetime.now().timestamp()
        self.tracker._handle_mouse_event(mouse_event)
        
        # Get current stats
        stats = self.tracker.get_current_stats()
        self.assertIn('current_window', stats)
        
        cognitive_load = self.tracker._calculate_cognitive_load()
        self.assertIsInstance(cognitive_load, dict)
        self.assertIn('overall_score', cognitive_load)
        self.assertIn('domain_scores', cognitive_load)

if __name__ == '__main__':
    unittest.main()
