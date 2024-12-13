"""
Integration module for Cognitive Acceleration Tracking
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Optional
from .cognitive_acceleration_tracker import CognitiveAccelerationTracker
from ..monitoring.cognitive_tracker import CognitiveInteractionTracker

class AccelerationIntegration:
    def __init__(self, cognitive_tracker: CognitiveInteractionTracker):
        self.logger = logging.getLogger(__name__)
        self.cognitive_tracker = cognitive_tracker
        self.acceleration_tracker = CognitiveAccelerationTracker()
        self.last_analysis_time = None
        self.analysis_interval = 60  # Analyze every 60 seconds
        
    async def start_tracking(self):
        """Start acceleration tracking"""
        try:
            self.logger.info("Starting acceleration tracking...")
            while True:
                current_time = datetime.now()
                
                if (self.last_analysis_time is None or 
                    (current_time - self.last_analysis_time).total_seconds() >= self.analysis_interval):
                    
                    # Get current cognitive metrics
                    metrics = self.cognitive_tracker.cognitive_metrics
                    
                    # Process acceleration
                    acceleration_data = await self.process_acceleration(metrics)
                    
                    if acceleration_data:
                        self.logger.info(f"Acceleration data: {acceleration_data}")
                    
                    self.last_analysis_time = current_time
                
                await asyncio.sleep(1)  # Check every second
                
        except Exception as e:
            self.logger.error(f"Error in acceleration tracking: {e}")
            raise
    
    async def process_acceleration(self, metrics: Dict) -> Optional[Dict]:
        """Process cognitive metrics for acceleration analysis"""
        try:
            # Prepare input stream
            input_stream = self._prepare_input_stream(metrics)
            
            # Track acceleration
            acceleration_data = await self.acceleration_tracker.track_realtime_acceleration(
                input_stream
            )
            
            # Calculate human-AI synergy
            synergy_factor = self.acceleration_tracker.calculate_cognitive_synergy(
                self._extract_human_patterns(metrics),
                self._extract_ai_patterns(metrics)
            )
            
            acceleration_data['synergy_factor'] = synergy_factor
            
            return acceleration_data
            
        except Exception as e:
            self.logger.error(f"Error processing acceleration: {e}")
            return None
    
    def _prepare_input_stream(self, metrics: Dict) -> Dict:
        """Prepare metrics for acceleration analysis"""
        try:
            return {
                'typing_metrics': {
                    'speed': metrics.get('typing_speed', []),
                    'error_rate': metrics.get('error_rate', []),
                    'pause_patterns': metrics.get('pause_patterns', [])
                },
                'cognitive_metrics': {
                    'focus_duration': metrics.get('focus_duration', []),
                    'task_switches': metrics.get('task_switches', []),
                    'activity_complexity': metrics.get('activity_complexity', [])
                },
                'learning_metrics': {
                    'vocabulary_usage': metrics.get('vocabulary_usage', {}),
                    'repeated_actions': metrics.get('repeated_actions', {}),
                    'error_corrections': metrics.get('error_corrections', [])
                }
            }
        except Exception as e:
            self.logger.error(f"Error preparing input stream: {e}")
            return {}
    
    def _extract_human_patterns(self, metrics: Dict) -> Dict:
        """Extract human interaction patterns"""
        try:
            return {
                'typing_patterns': {
                    'speed_progression': self._calculate_progression(metrics.get('typing_speed', [])),
                    'error_reduction': self._calculate_progression(metrics.get('error_rate', []), inverse=True)
                },
                'learning_patterns': {
                    'vocabulary_growth': len(metrics.get('vocabulary_usage', {})),
                    'action_refinement': len(metrics.get('repeated_actions', {}))
                },
                'cognitive_patterns': {
                    'focus_improvement': self._calculate_progression(metrics.get('focus_duration', [])),
                    'complexity_handling': self._calculate_progression(metrics.get('activity_complexity', []))
                }
            }
        except Exception as e:
            self.logger.error(f"Error extracting human patterns: {e}")
            return {}
    
    def _extract_ai_patterns(self, metrics: Dict) -> Dict:
        """Extract AI assistance patterns"""
        try:
            return {
                'assistance_patterns': {
                    'suggestion_accuracy': self._calculate_suggestion_accuracy(metrics),
                    'adaptation_speed': self._calculate_adaptation_speed(metrics)
                },
                'interaction_patterns': {
                    'response_refinement': self._calculate_response_refinement(metrics),
                    'context_understanding': self._calculate_context_understanding(metrics)
                }
            }
        except Exception as e:
            self.logger.error(f"Error extracting AI patterns: {e}")
            return {}
    
    def _calculate_progression(self, values: list, inverse: bool = False) -> float:
        """Calculate progression rate from a series of values"""
        try:
            if not values or len(values) < 2:
                return 0.0
            
            recent_values = values[-10:]  # Look at last 10 values
            if inverse:
                recent_values = [1 - v for v in recent_values]
            
            progression = (recent_values[-1] - recent_values[0]) / len(recent_values)
            return max(0.0, progression)  # Ensure non-negative progression
            
        except Exception as e:
            self.logger.error(f"Error calculating progression: {e}")
            return 0.0
