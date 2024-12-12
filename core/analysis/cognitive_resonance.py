"""
Cognitive Resonance Detection System
Implements the Cognitive Field Theory for pattern emergence and resonance detection.
"""

import numpy as np
from scipy import signal
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging
from datetime import datetime, timedelta
from .cognitive_patterns import CognitivePattern, TimeScale

class ResonanceType(Enum):
    LEARNING = "learning"          # Knowledge acquisition resonance
    INSIGHT = "insight"           # Pattern recognition resonance
    INTEGRATION = "integration"    # Knowledge integration resonance
    INNOVATION = "innovation"      # Novel pattern emergence

@dataclass
class CognitiveResonance:
    type: ResonanceType
    strength: float               # Resonance strength (0-1)
    duration: float              # Duration in seconds
    patterns: List[CognitivePattern]
    emergence_metrics: Dict[str, float]
    context: Dict[str, any]

class CognitiveFieldAnalyzer:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.resonance_history: List[CognitiveResonance] = []
        
    def detect_resonance(self, patterns: List[CognitivePattern]) -> Optional[CognitiveResonance]:
        """Detect cognitive resonance patterns in a sequence of cognitive patterns"""
        if not patterns or len(patterns) < 2:
            return None
            
        # Sort patterns by time
        patterns = sorted(patterns, key=lambda p: p.start_time)
        
        # Calculate resonance metrics
        metrics = self._calculate_resonance_metrics(patterns)
        
        # Detect resonance type and strength
        resonance_type, strength = self._classify_resonance(metrics)
        
        if strength > 0.6:  # Resonance threshold
            return CognitiveResonance(
                type=resonance_type,
                strength=strength,
                duration=patterns[-1].end_time - patterns[0].start_time,
                patterns=patterns,
                emergence_metrics=metrics,
                context=self._merge_contexts([p.context for p in patterns])
            )
        return None
        
    def _calculate_resonance_metrics(self, patterns: List[CognitivePattern]) -> Dict[str, float]:
        """Calculate metrics for resonance detection"""
        metrics = {}
        
        # Extract time series of key metrics
        times = np.array([p.start_time for p in patterns])
        times = times - times[0]  # Normalize to start at 0
        
        # Calculate cognitive load progression
        loads = np.array([p.metrics.get('cognitive_load', 0) for p in patterns])
        metrics['load_trend'] = np.polyfit(times, loads, 1)[0] if len(times) > 1 else 0
        
        # Calculate focus stability
        focus_durations = [p.metrics.get('avg_focus_duration', 0) for p in patterns]
        metrics['focus_stability'] = np.std(focus_durations)
        
        # Calculate pattern coherence
        pattern_types = [p.pattern_type for p in patterns]
        metrics['pattern_coherence'] = len(set(pattern_types)) / len(patterns)
        
        # Calculate rhythm metrics
        if len(times) > 1:
            intervals = np.diff(times)
            metrics['rhythm_regularity'] = 1.0 / (1.0 + np.std(intervals))
        else:
            metrics['rhythm_regularity'] = 0
            
        # Calculate emergence indicators
        metrics['emergence_potential'] = self._calculate_emergence_potential(patterns)
        
        return metrics
        
    def _calculate_emergence_potential(self, patterns: List[CognitivePattern]) -> float:
        """Calculate the potential for cognitive emergence"""
        if not patterns:
            return 0.0
            
        # Factors that indicate emergence potential
        factors = {
            'pattern_diversity': self._calculate_pattern_diversity(patterns),
            'interaction_complexity': self._calculate_interaction_complexity(patterns),
            'stability_metrics': self._calculate_stability_metrics(patterns),
            'novelty_score': self._calculate_novelty_score(patterns)
        }
        
        # Weighted combination of factors
        weights = {
            'pattern_diversity': 0.3,
            'interaction_complexity': 0.2,
            'stability_metrics': 0.2,
            'novelty_score': 0.3
        }
        
        return sum(score * weights[factor] for factor, score in factors.items())
        
    def _calculate_pattern_diversity(self, patterns: List[CognitivePattern]) -> float:
        """Calculate diversity of cognitive patterns"""
        pattern_types = [p.pattern_type for p in patterns]
        unique_patterns = len(set(pattern_types))
        return unique_patterns / len(patterns) if patterns else 0
        
    def _calculate_interaction_complexity(self, patterns: List[CognitivePattern]) -> float:
        """Calculate complexity of interactions between patterns"""
        if len(patterns) < 2:
            return 0.0
            
        # Calculate transition probabilities between pattern types
        transitions = {}
        for i in range(len(patterns) - 1):
            key = (patterns[i].pattern_type, patterns[i + 1].pattern_type)
            transitions[key] = transitions.get(key, 0) + 1
            
        # Normalize transitions
        total = sum(transitions.values())
        entropy = -sum((count/total) * np.log2(count/total) 
                      for count in transitions.values())
                      
        # Normalize to 0-1 range
        max_entropy = np.log2(len(transitions))
        return entropy / max_entropy if max_entropy > 0 else 0
        
    def _calculate_stability_metrics(self, patterns: List[CognitivePattern]) -> float:
        """Calculate stability metrics for pattern sequence"""
        if not patterns:
            return 0.0
            
        # Calculate consistency of key metrics over time
        metric_stabilities = []
        for metric in ['typing_speed', 'error_rate', 'focus_switches']:
            values = [p.metrics.get(metric, 0) for p in patterns]
            if values:
                stability = 1.0 / (1.0 + np.std(values))
                metric_stabilities.append(stability)
                
        return np.mean(metric_stabilities) if metric_stabilities else 0
        
    def _calculate_novelty_score(self, patterns: List[CognitivePattern]) -> float:
        """Calculate novelty score for pattern sequence"""
        if not patterns:
            return 0.0
            
        # Compare current patterns with historical resonances
        if not self.resonance_history:
            return 1.0  # Maximum novelty if no history
            
        # Calculate similarity with historical patterns
        similarities = []
        for resonance in self.resonance_history[-10:]:  # Compare with last 10 resonances
            similarity = self._pattern_sequence_similarity(patterns, resonance.patterns)
            similarities.append(similarity)
            
        # Novelty is inverse of maximum similarity
        return 1.0 - (max(similarities) if similarities else 0)
        
    def _pattern_sequence_similarity(self, patterns1: List[CognitivePattern], 
                                   patterns2: List[CognitivePattern]) -> float:
        """Calculate similarity between two pattern sequences"""
        # Compare pattern types
        types1 = [p.pattern_type for p in patterns1]
        types2 = [p.pattern_type for p in patterns2]
        
        # Use Levenshtein distance for sequence similarity
        distance = self._levenshtein_distance(types1, types2)
        max_length = max(len(types1), len(types2))
        
        return 1.0 - (distance / max_length if max_length > 0 else 0)
        
    def _levenshtein_distance(self, seq1: List[str], seq2: List[str]) -> int:
        """Calculate Levenshtein distance between two sequences"""
        size_x = len(seq1) + 1
        size_y = len(seq2) + 1
        matrix = np.zeros((size_x, size_y))
        
        for x in range(size_x):
            matrix[x, 0] = x
        for y in range(size_y):
            matrix[0, y] = y
            
        for x in range(1, size_x):
            for y in range(1, size_y):
                if seq1[x-1] == seq2[y-1]:
                    matrix[x,y] = min(
                        matrix[x-1, y] + 1,
                        matrix[x-1, y-1],
                        matrix[x, y-1] + 1
                    )
                else:
                    matrix[x,y] = min(
                        matrix[x-1,y] + 1,
                        matrix[x-1,y-1] + 1,
                        matrix[x,y-1] + 1
                    )
        return matrix[size_x-1, size_y-1]
        
    def _classify_resonance(self, metrics: Dict[str, float]) -> Tuple[ResonanceType, float]:
        """Classify the type and strength of cognitive resonance"""
        # Resonance type classification rules
        type_rules = {
            ResonanceType.LEARNING: {
                'conditions': {
                    'load_trend': (lambda x: x > 0),  # Increasing cognitive load
                    'focus_stability': (lambda x: x < 0.5),  # Some variability in focus
                    'pattern_coherence': (lambda x: x > 0.6),  # Coherent patterns
                    'emergence_potential': (lambda x: 0.3 < x < 0.7)  # Moderate emergence
                },
                'weights': {
                    'load_trend': 0.3,
                    'focus_stability': 0.2,
                    'pattern_coherence': 0.3,
                    'emergence_potential': 0.2
                }
            },
            ResonanceType.INSIGHT: {
                'conditions': {
                    'load_trend': (lambda x: x < 0),  # Decreasing cognitive load
                    'focus_stability': (lambda x: x > 0.7),  # Stable focus
                    'pattern_coherence': (lambda x: x > 0.8),  # Very coherent patterns
                    'emergence_potential': (lambda x: x > 0.7)  # High emergence
                },
                'weights': {
                    'load_trend': 0.2,
                    'focus_stability': 0.3,
                    'pattern_coherence': 0.2,
                    'emergence_potential': 0.3
                }
            },
            ResonanceType.INTEGRATION: {
                'conditions': {
                    'load_trend': (lambda x: -0.2 < x < 0.2),  # Stable cognitive load
                    'focus_stability': (lambda x: x > 0.5),  # Moderately stable focus
                    'pattern_coherence': (lambda x: 0.4 < x < 0.8),  # Mixed patterns
                    'emergence_potential': (lambda x: 0.4 < x < 0.8)  # Moderate emergence
                },
                'weights': {
                    'load_trend': 0.25,
                    'focus_stability': 0.25,
                    'pattern_coherence': 0.25,
                    'emergence_potential': 0.25
                }
            },
            ResonanceType.INNOVATION: {
                'conditions': {
                    'load_trend': (lambda x: x > 0.2),  # Increasing cognitive load
                    'focus_stability': (lambda x: x < 0.3),  # Variable focus
                    'pattern_coherence': (lambda x: x < 0.5),  # Diverse patterns
                    'emergence_potential': (lambda x: x > 0.8)  # Very high emergence
                },
                'weights': {
                    'load_trend': 0.2,
                    'focus_stability': 0.2,
                    'pattern_coherence': 0.2,
                    'emergence_potential': 0.4
                }
            }
        }
        
        # Calculate confidence for each resonance type
        confidences = {}
        for res_type, config in type_rules.items():
            confidence = 0
            for metric, condition in config['conditions'].items():
                if metric in metrics:
                    weight = config['weights'][metric]
                    if condition(metrics[metric]):
                        confidence += weight
            confidences[res_type] = confidence
            
        # Select resonance type with highest confidence
        best_resonance = max(confidences.items(), key=lambda x: x[1])
        return best_resonance[0], best_resonance[1]
        
    def _merge_contexts(self, contexts: List[Dict]) -> Dict:
        """Merge multiple context dictionaries"""
        if not contexts:
            return {}
            
        # Start with the most recent context
        merged = contexts[-1].copy()
        
        # Add unique information from older contexts
        for context in reversed(contexts[:-1]):
            for key, value in context.items():
                if key not in merged:
                    merged[key] = value
                    
        return merged
