"""
Tests for the Cognitive Acceleration Tracker
"""

import unittest
import asyncio
from datetime import datetime, timedelta
import numpy as np
from core.acceleration.cognitive_acceleration_tracker import (
    CognitiveAccelerationTracker,
    CognitiveAccelerationMetrics,
    AccelerationVector
)

class TestCognitiveAccelerationTracker(unittest.TestCase):
    def setUp(self):
        self.tracker = CognitiveAccelerationTracker()
        
        # Setup test data
        self.test_input_stream = {
            'typing_metrics': {
                'speed': [40, 45, 50, 55, 60],  # WPM
                'error_rate': [0.1, 0.08, 0.06, 0.05, 0.04],
                'pause_patterns': [1.2, 1.0, 0.9, 0.8, 0.7]  # seconds
            },
            'cognitive_metrics': {
                'focus_duration': [300, 350, 400, 450, 500],  # seconds
                'task_switches': [10, 8, 7, 6, 5],  # per hour
                'activity_complexity': [0.5, 0.6, 0.7, 0.8, 0.9]
            },
            'learning_metrics': {
                'vocabulary_usage': {'word1': 1, 'word2': 2, 'word3': 3},
                'repeated_actions': {'action1': 5, 'action2': 3},
                'error_corrections': [5, 4, 3, 2, 1]
            }
        }
    
    async def test_track_realtime_acceleration(self):
        """Test realtime acceleration tracking"""
        result = await self.tracker.track_realtime_acceleration(self.test_input_stream)
        
        # Verify structure
        self.assertIn('current_acceleration', result)
        self.assertIn('pattern_evolution', result)
        self.assertIn('growth_trajectory', result)
        self.assertIn('meta_patterns', result)
        
        # Verify acceleration calculations
        acceleration = result['current_acceleration']
        self.assertTrue(all(isinstance(v, float) for v in acceleration.values()))
        
        # Verify pattern evolution
        evolution = result['pattern_evolution']
        self.assertGreater(evolution['recognition_speed'], 0)
        self.assertGreater(evolution['integration_speed'], 0)
        
    def test_extract_base_patterns(self):
        """Test base pattern extraction"""
        patterns = self.tracker.extract_base_patterns(self.test_input_stream)
        
        self.assertIn('typing_speed', patterns)
        self.assertIn('error_recovery', patterns)
        self.assertIn('context_switching', patterns)
        self.assertIn('problem_solving', patterns)
        
        # Verify pattern memory
        self.assertTrue(all(len(v) > 0 for v in self.tracker.pattern_memory.values()))
        
    def test_calculate_acceleration(self):
        """Test acceleration calculation"""
        base_patterns = self.tracker.extract_base_patterns(self.test_input_stream)
        acceleration = self.tracker.calculate_acceleration(base_patterns)
        
        # Verify acceleration values
        self.assertTrue(all(isinstance(v, float) for v in acceleration.values()))
        
    def test_track_pattern_evolution(self):
        """Test pattern evolution tracking"""
        base_patterns = self.tracker.extract_base_patterns(self.test_input_stream)
        evolution = self.tracker.track_pattern_evolution(base_patterns)
        
        self.assertIn('recognition_speed', evolution)
        self.assertIn('integration_speed', evolution)
        self.assertIn('pattern_complexity', evolution)
        
    def test_analyze_growth_trajectory(self):
        """Test growth trajectory analysis"""
        base_patterns = self.tracker.extract_base_patterns(self.test_input_stream)
        acceleration = self.tracker.calculate_acceleration(base_patterns)
        evolution = self.tracker.track_pattern_evolution(base_patterns)
        
        growth = self.tracker.analyze_growth_trajectory(acceleration, evolution)
        
        self.assertIn('acceleration_trend', growth)
        self.assertIn('learning_efficiency', growth)
        self.assertIn('adaptability', growth)
        
    def test_calculate_cognitive_synergy(self):
        """Test cognitive synergy calculation"""
        human_patterns = {
            'typing_patterns': {
                'speed_progression': 0.8,
                'error_reduction': 0.7
            },
            'learning_patterns': {
                'vocabulary_growth': 100,
                'action_refinement': 50
            }
        }
        
        ai_patterns = {
            'assistance_patterns': {
                'suggestion_accuracy': 0.9,
                'adaptation_speed': 0.8
            },
            'interaction_patterns': {
                'response_refinement': 0.85,
                'context_understanding': 0.9
            }
        }
        
        synergy = self.tracker.calculate_cognitive_synergy(human_patterns, ai_patterns)
        
        self.assertIsInstance(synergy, float)
        self.assertGreaterEqual(synergy, 0.0)
        self.assertLessEqual(synergy, 1.0)

if __name__ == '__main__':
    unittest.main()
