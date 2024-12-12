"""
Cognitive Pattern Analysis System
Implements multi-scale temporal analysis of cognitive states and patterns.
"""

import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import pandas as pd
from dataclasses import dataclass
from enum import Enum
import json
from pathlib import Path
import logging

class TimeScale(Enum):
    MICRO = "micro"  # seconds to minutes
    MESO = "meso"    # minutes to hours
    MACRO = "macro"  # days to weeks

@dataclass
class CognitiveState:
    timestamp: float
    attention_level: float
    cognitive_load: float
    task_engagement: float
    context: Dict[str, any]
    
@dataclass
class CognitivePattern:
    scale: TimeScale
    start_time: float
    end_time: float
    pattern_type: str
    confidence: float
    metrics: Dict[str, float]
    context: Dict[str, any]

class CognitivePatternAnalyzer:
    def __init__(self, log_dir: str = "interaction_logs"):
        self.logger = logging.getLogger(__name__)
        self.log_dir = Path(log_dir)
        self.patterns: Dict[TimeScale, List[CognitivePattern]] = {
            TimeScale.MICRO: [],
            TimeScale.MESO: [],
            TimeScale.MACRO: []
        }
        
    def analyze_micro_patterns(self, events: List[Dict]) -> List[CognitivePattern]:
        """Analyze micro-scale patterns (seconds to minutes)"""
        patterns = []
        
        # Group events by time windows
        window_size = timedelta(minutes=1)
        current_window = []
        last_timestamp = None
        
        for event in events:
            event_time = datetime.fromtimestamp(event['timestamp'])
            
            if last_timestamp and event_time - last_timestamp > window_size:
                # Analyze completed window
                if current_window:
                    pattern = self._analyze_micro_window(current_window)
                    if pattern:
                        patterns.append(pattern)
                current_window = []
            
            current_window.append(event)
            last_timestamp = event_time
            
        return patterns
        
    def analyze_meso_patterns(self, micro_patterns: List[CognitivePattern]) -> List[CognitivePattern]:
        """Analyze meso-scale patterns (minutes to hours)"""
        patterns = []
        
        # Group micro patterns into larger time windows
        window_size = timedelta(hours=1)
        current_window = []
        last_pattern = None
        
        for pattern in micro_patterns:
            pattern_time = datetime.fromtimestamp(pattern.start_time)
            
            if last_pattern and pattern_time - datetime.fromtimestamp(last_pattern.start_time) > window_size:
                # Analyze completed window
                if current_window:
                    meso_pattern = self._analyze_meso_window(current_window)
                    if meso_pattern:
                        patterns.append(meso_pattern)
                current_window = []
            
            current_window.append(pattern)
            last_pattern = pattern
            
        return patterns
        
    def analyze_macro_patterns(self, meso_patterns: List[CognitivePattern]) -> List[CognitivePattern]:
        """Analyze macro-scale patterns (days to weeks)"""
        patterns = []
        
        # Group meso patterns into larger time windows
        window_size = timedelta(days=1)
        current_window = []
        last_pattern = None
        
        for pattern in meso_patterns:
            pattern_time = datetime.fromtimestamp(pattern.start_time)
            
            if last_pattern and pattern_time - datetime.fromtimestamp(last_pattern.start_time) > window_size:
                # Analyze completed window
                if current_window:
                    macro_pattern = self._analyze_macro_window(current_window)
                    if macro_pattern:
                        patterns.append(macro_pattern)
                current_window = []
            
            current_window.append(pattern)
            last_pattern = pattern
            
        return patterns
        
    def _analyze_micro_window(self, events: List[Dict]) -> Optional[CognitivePattern]:
        """Analyze a micro-scale window of events"""
        if not events:
            return None
            
        # Calculate metrics
        timestamps = [e['timestamp'] for e in events]
        start_time = min(timestamps)
        end_time = max(timestamps)
        
        # Analyze typing patterns
        typing_events = [e for e in events if e['type'] == 'keyboard']
        typing_metrics = self._analyze_typing_pattern(typing_events)
        
        # Analyze focus patterns
        focus_events = [e for e in events if e['type'] in ['mouse', 'window']]
        focus_metrics = self._analyze_focus_pattern(focus_events)
        
        # Combine metrics
        metrics = {**typing_metrics, **focus_metrics}
        
        # Determine pattern type and confidence
        pattern_type, confidence = self._classify_micro_pattern(metrics)
        
        return CognitivePattern(
            scale=TimeScale.MICRO,
            start_time=start_time,
            end_time=end_time,
            pattern_type=pattern_type,
            confidence=confidence,
            metrics=metrics,
            context=self._extract_context(events)
        )
        
    def _analyze_typing_pattern(self, events: List[Dict]) -> Dict[str, float]:
        """Analyze typing patterns within events"""
        if not events:
            return {'typing_speed': 0.0, 'error_rate': 0.0, 'pause_ratio': 0.0}
            
        # Calculate typing speed
        char_count = len([e for e in events if e['event_type'] == 'down'])
        duration = events[-1]['timestamp'] - events[0]['timestamp']
        typing_speed = char_count / duration if duration > 0 else 0
        
        # Calculate error rate (backspaces/deletes)
        error_count = len([e for e in events if e['key'] in ['backspace', 'delete']])
        error_rate = error_count / char_count if char_count > 0 else 0
        
        # Calculate pause ratio
        pauses = []
        for i in range(1, len(events)):
            pause = events[i]['timestamp'] - events[i-1]['timestamp']
            if pause > 1.0:  # Pause threshold of 1 second
                pauses.append(pause)
        pause_ratio = sum(pauses) / duration if duration > 0 else 0
        
        return {
            'typing_speed': typing_speed,
            'error_rate': error_rate,
            'pause_ratio': pause_ratio
        }
        
    def _analyze_focus_pattern(self, events: List[Dict]) -> Dict[str, float]:
        """Analyze focus patterns within events"""
        if not events:
            return {'focus_switches': 0.0, 'avg_focus_duration': 0.0}
            
        # Count window switches
        window_changes = [i for i in range(1, len(events))
                         if events[i].get('window_info', {}).get('title') !=
                         events[i-1].get('window_info', {}).get('title')]
        
        # Calculate average focus duration
        focus_durations = []
        last_switch = 0
        for switch in window_changes + [len(events)]:
            duration = events[switch]['timestamp'] - events[last_switch]['timestamp']
            focus_durations.append(duration)
            last_switch = switch
            
        return {
            'focus_switches': len(window_changes),
            'avg_focus_duration': np.mean(focus_durations) if focus_durations else 0.0
        }
        
    def _classify_micro_pattern(self, metrics: Dict[str, float]) -> Tuple[str, float]:
        """Classify the type of micro pattern based on metrics"""
        # Define pattern types
        patterns = {
            'flow_state': {
                'conditions': {
                    'typing_speed': (lambda x: x > 2.0),  # chars per second
                    'error_rate': (lambda x: x < 0.1),    # 10% error rate
                    'pause_ratio': (lambda x: x < 0.2),   # 20% time in pauses
                    'focus_switches': (lambda x: x < 2),  # fewer than 2 switches per minute
                },
                'weights': {
                    'typing_speed': 0.3,
                    'error_rate': 0.2,
                    'pause_ratio': 0.2,
                    'focus_switches': 0.3
                }
            },
            'learning_moment': {
                'conditions': {
                    'typing_speed': (lambda x: 0.5 < x < 2.0),
                    'error_rate': (lambda x: 0.1 < x < 0.3),
                    'pause_ratio': (lambda x: 0.2 < x < 0.4),
                    'focus_switches': (lambda x: 2 < x < 5)
                },
                'weights': {
                    'typing_speed': 0.2,
                    'error_rate': 0.3,
                    'pause_ratio': 0.3,
                    'focus_switches': 0.2
                }
            },
            'confusion_state': {
                'conditions': {
                    'typing_speed': (lambda x: x < 0.5),
                    'error_rate': (lambda x: x > 0.3),
                    'pause_ratio': (lambda x: x > 0.4),
                    'focus_switches': (lambda x: x > 5)
                },
                'weights': {
                    'typing_speed': 0.2,
                    'error_rate': 0.3,
                    'pause_ratio': 0.2,
                    'focus_switches': 0.3
                }
            }
        }
        
        # Calculate confidence for each pattern type
        confidences = {}
        for pattern_type, config in patterns.items():
            confidence = 0
            for metric, condition in config['conditions'].items():
                if metric in metrics:
                    weight = config['weights'][metric]
                    if condition(metrics[metric]):
                        confidence += weight
            confidences[pattern_type] = confidence
            
        # Select pattern with highest confidence
        best_pattern = max(confidences.items(), key=lambda x: x[1])
        return best_pattern[0], best_pattern[1]
        
    def _extract_context(self, events: List[Dict]) -> Dict[str, any]:
        """Extract context information from events"""
        if not events:
            return {}
            
        # Get the most common window context
        window_contexts = [e.get('window_info', {}) for e in events]
        if window_contexts:
            return max(window_contexts, key=window_contexts.count)
        return {}
