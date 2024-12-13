"""
Tests for the MetaCognitive Analyzer
"""

import unittest
from datetime import datetime
from core.analysis.metacognitive_analyzer import MetaCognitiveAnalyzer, AwarenessState, InsightPattern

class TestMetaCognitiveAnalyzer(unittest.TestCase):
    def setUp(self):
        self.analyzer = MetaCognitiveAnalyzer()
        
        # Setup test states
        self.initial_state = {
            'awareness_level': 0.5,
            'understanding': {
                'python': {'depth': 0.6},
                'algorithms': {'depth': 0.4}
            },
            'concept_patterns': {
                'basic_programming': 0.7,
                'data_structures': 0.5
            }
        }
        
        self.current_state = {
            'awareness_level': 0.8,
            'understanding': {
                'python': {'depth': 0.9},
                'algorithms': {'depth': 0.7},
                'machine_learning': {'depth': 0.4}
            },
            'concept_patterns': {
                'basic_programming': 0.9,
                'data_structures': 0.8,
                'neural_networks': 0.6
            }
        }
        
    def test_analyze_cognitive_evolution(self):
        """Test cognitive evolution analysis"""
        result = self.analyzer.analyze_cognitive_evolution(
            self.initial_state, 
            self.current_state
        )
        
        # Verify structure
        self.assertIn('cognitive_expansion', result)
        self.assertIn('awareness_patterns', result)
        self.assertIn('meta_patterns', result)
        
        # Verify cognitive expansion
        expansion = result['cognitive_expansion']
        self.assertIsInstance(expansion['depth_increase'], float)
        self.assertIsInstance(expansion['breadth_increase'], float)
        self.assertIsInstance(expansion['integration_level'], float)
        
    def test_track_insight_patterns(self):
        """Test insight pattern tracking"""
        insights = self.analyzer.track_insight_patterns(
            self.initial_state,
            self.current_state
        )
        
        # Should detect new machine_learning domain
        self.assertTrue(any(
            insight['domain'] == 'machine_learning' 
            and insight['type'] == 'new_domain'
            for insight in insights
        ))
        
        # Should detect depth increase in python
        self.assertTrue(any(
            insight['domain'] == 'python'
            and insight['type'] == 'depth_increase'
            for insight in insights
        ))
        
    def test_map_awareness_evolution(self):
        """Test awareness evolution mapping"""
        evolution = self.analyzer.map_awareness_evolution(
            self.initial_state['awareness_level'],
            self.current_state['awareness_level']
        )
        
        self.assertIn('quantitative_growth', evolution)
        self.assertEqual(
            evolution['quantitative_growth'],
            self.current_state['awareness_level'] - self.initial_state['awareness_level']
        )
        
    def test_measure_curiosity_growth(self):
        """Test curiosity growth measurement"""
        growth = self.analyzer.measure_curiosity_growth()
        
        self.assertIn('curiosity_depth', growth)
        self.assertIn('exploration_breadth', growth)
        self.assertIn('question_complexity', growth)
        self.assertIn('insight_triggers', growth)
        
    def test_analyze_transformation_points(self):
        """Test transformation point analysis"""
        # Add some test states
        self.analyzer.awareness_states.append(
            AwarenessState(
                timestamp=datetime.now(),
                level=0.5,
                domains=['python'],
                active_concepts={'basic_programming': 0.7},
                integration_score=0.6
            )
        )
        
        transformations = self.analyzer.analyze_transformation_points()
        self.assertIsInstance(transformations, list)
        
if __name__ == '__main__':
    unittest.main()
