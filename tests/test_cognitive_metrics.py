"""
Unit tests for cognitive metrics calculations and analysis.
"""

import unittest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
from core.monitoring.cognitive_tracker import CognitiveInteractionTracker

class TestCognitiveMetrics(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.tracker = CognitiveInteractionTracker()
        self.mock_events = []

    def test_memory_metrics(self):
        """Test metrics related to memory domain."""
        # Simulate repeated incorrect folder access
        folder_events = [
            {'type': 'file_access', 'path': '/wrong/folder1', 'timestamp': datetime.now()},
            {'type': 'file_access', 'path': '/wrong/folder2', 'timestamp': datetime.now()},
            {'type': 'file_access', 'path': '/correct/folder', 'timestamp': datetime.now()}
        ]
        memory_metrics = self.tracker._analyze_memory_patterns(folder_events)
        
        self.assertIn('incorrect_folder_attempts', memory_metrics)
        self.assertIn('repeated_access_count', memory_metrics)
        self.assertEqual(memory_metrics['incorrect_folder_attempts'], 2)

    def test_executive_function_metrics(self):
        """Test metrics related to executive function domain."""
        # Simulate multitasking behavior
        window_events = [
            {'type': 'window_switch', 'window_title': 'App1', 'timestamp': datetime.now()},
            {'type': 'window_switch', 'window_title': 'App2', 'timestamp': datetime.now()},
            {'type': 'window_switch', 'window_title': 'App1', 'timestamp': datetime.now()}
        ]
        exec_metrics = self.tracker._analyze_executive_function(window_events)
        
        self.assertIn('task_switching_frequency', exec_metrics)
        self.assertIn('multitasking_score', exec_metrics)
        self.assertGreaterEqual(exec_metrics['task_switching_frequency'], 0)

    def test_language_metrics(self):
        """Test metrics related to language domain."""
        # Simulate typing behavior
        typing_events = [
            {'type': 'keyboard', 'key': 'a', 'event_type': 'down', 'timestamp': datetime.now()},
            {'type': 'keyboard', 'key': 'backspace', 'event_type': 'down', 'timestamp': datetime.now()},
            {'type': 'keyboard', 'key': 'b', 'event_type': 'down', 'timestamp': datetime.now()}
        ]
        language_metrics = self.tracker._analyze_language_patterns(typing_events)
        
        self.assertIn('typing_speed', language_metrics)
        self.assertIn('error_correction_rate', language_metrics)
        self.assertIn('vocabulary_complexity', language_metrics)

    def test_perception_action_metrics(self):
        """Test metrics related to perception and action domain."""
        # Simulate mouse movement and clicks
        mouse_events = [
            {'type': 'mouse', 'event_type': 'move', 'position': (100, 100), 'timestamp': datetime.now()},
            {'type': 'mouse', 'event_type': 'click', 'position': (120, 120), 'timestamp': datetime.now()},
            {'type': 'mouse', 'event_type': 'move', 'position': (150, 150), 'timestamp': datetime.now()}
        ]
        perception_metrics = self.tracker._analyze_perception_action(mouse_events)
        
        self.assertIn('mouse_precision', perception_metrics)
        self.assertIn('click_accuracy', perception_metrics)
        self.assertIn('movement_smoothness', perception_metrics)

    def test_usage_pattern_metrics(self):
        """Test metrics related to overall usage patterns."""
        # Simulate daily usage data
        usage_data = {
            datetime.now().date(): {'duration': 3600, 'active_windows': 5},
            (datetime.now() - timedelta(days=1)).date(): {'duration': 3200, 'active_windows': 4},
            (datetime.now() - timedelta(days=2)).date(): {'duration': 3400, 'active_windows': 6}
        }
        pattern_metrics = self.tracker._analyze_usage_patterns(usage_data)
        
        self.assertIn('daily_usage_variance', pattern_metrics)
        self.assertIn('activity_complexity', pattern_metrics)
        self.assertIn('usage_trend', pattern_metrics)

    def test_cognitive_load_calculation(self):
        """Test overall cognitive load calculation."""
        # Mock various metrics
        metrics = {
            'memory': {'score': 0.8},
            'executive': {'score': 0.7},
            'language': {'score': 0.9},
            'perception': {'score': 0.85}
        }
        
        cognitive_load = self.tracker._calculate_cognitive_load(metrics)
        
        self.assertGreaterEqual(cognitive_load['overall_score'], 0)
        self.assertLessEqual(cognitive_load['overall_score'], 1)
        self.assertIn('domain_scores', cognitive_load)

    def test_behavioral_change_detection(self):
        """Test detection of significant behavioral changes."""
        # Simulate historical vs current metrics
        historical_metrics = {
            'typing_speed': 60,
            'error_rate': 0.05,
            'task_switching_frequency': 10
        }
        current_metrics = {
            'typing_speed': 45,
            'error_rate': 0.08,
            'task_switching_frequency': 7
        }
        
        changes = self.tracker._detect_behavioral_changes(historical_metrics, current_metrics)
        
        self.assertIn('significant_changes', changes)
        self.assertIn('change_severity', changes)
        self.assertTrue(isinstance(changes['significant_changes'], list))

if __name__ == '__main__':
    unittest.main()
