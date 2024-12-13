"""
Integration module for MetaCognitive Analysis with Cognitive Tracker
"""

import logging
from datetime import datetime
from typing import Dict, Optional
from ..analysis.metacognitive_analyzer import MetaCognitiveAnalyzer
from ..monitoring.cognitive_tracker import CognitiveInteractionTracker

class MetaCognitiveIntegration:
    def __init__(self, cognitive_tracker: CognitiveInteractionTracker):
        self.logger = logging.getLogger(__name__)
        self.cognitive_tracker = cognitive_tracker
        self.meta_analyzer = MetaCognitiveAnalyzer()
        self.last_analysis_time = None
        self.initial_state = None
        
    def process_cognitive_state(self, current_metrics: Dict) -> Optional[Dict]:
        """Process current cognitive state and generate meta-analysis"""
        try:
            current_time = datetime.now()
            
            # Initialize if first run
            if self.initial_state is None:
                self.initial_state = self._prepare_cognitive_state(current_metrics)
                self.last_analysis_time = current_time
                return None
            
            # Prepare current state
            current_state = self._prepare_cognitive_state(current_metrics)
            
            # Analyze cognitive evolution
            analysis_result = self.meta_analyzer.analyze_cognitive_evolution(
                self.initial_state,
                current_state
            )
            
            # Update last analysis time
            self.last_analysis_time = current_time
            
            return analysis_result
            
        except Exception as e:
            self.logger.error(f"Error processing cognitive state: {e}")
            return None
    
    def _prepare_cognitive_state(self, metrics: Dict) -> Dict:
        """Prepare cognitive state from metrics"""
        try:
            return {
                'awareness_level': self._calculate_awareness_level(metrics),
                'understanding': self._extract_understanding_patterns(metrics),
                'concept_patterns': self._extract_concept_patterns(metrics)
            }
        except Exception as e:
            self.logger.error(f"Error preparing cognitive state: {e}")
            return {}
    
    def _calculate_awareness_level(self, metrics: Dict) -> float:
        """Calculate current awareness level from metrics"""
        try:
            # Combine multiple metrics to estimate awareness
            focus_score = metrics.get('focus_duration', [0])[-1] if metrics.get('focus_duration') else 0
            error_rate = metrics.get('error_rate', [0])[-1] if metrics.get('error_rate') else 0
            typing_speed = metrics.get('typing_speed', [0])[-1] if metrics.get('typing_speed') else 0
            
            # Normalize and combine scores
            normalized_focus = min(focus_score / 3600, 1.0)  # Normalize to 1 hour
            normalized_accuracy = 1.0 - min(error_rate, 1.0)
            normalized_speed = min(typing_speed / 100, 1.0)  # Normalize to 100 WPM
            
            # Weighted combination
            awareness = (
                0.5 * normalized_focus +
                0.3 * normalized_accuracy +
                0.2 * normalized_speed
            )
            
            return min(max(awareness, 0.0), 1.0)
            
        except Exception as e:
            self.logger.error(f"Error calculating awareness level: {e}")
            return 0.0
    
    def _extract_understanding_patterns(self, metrics: Dict) -> Dict:
        """Extract understanding patterns from metrics"""
        try:
            understanding = {}
            
            # Extract patterns from different domains
            if 'activity_complexity' in metrics:
                understanding['coding'] = {
                    'depth': metrics['activity_complexity'][-1] if metrics['activity_complexity'] else 0.0
                }
            
            if 'language_usage' in metrics:
                understanding['language'] = {
                    'depth': len(metrics['language_usage']) / 100  # Normalize by expected vocabulary size
                }
                
            return understanding
            
        except Exception as e:
            self.logger.error(f"Error extracting understanding patterns: {e}")
            return {}
    
    def _extract_concept_patterns(self, metrics: Dict) -> Dict:
        """Extract concept patterns from metrics"""
        try:
            concepts = {}
            
            # Extract concept familiarity from interaction patterns
            if 'folder_access_patterns' in metrics:
                concepts['navigation'] = len(metrics['folder_access_patterns']) / 50  # Normalize
                
            if 'repeated_actions' in metrics:
                concepts['workflow'] = len(metrics['repeated_actions']) / 20  # Normalize
                
            return concepts
            
        except Exception as e:
            self.logger.error(f"Error extracting concept patterns: {e}")
            return {}
