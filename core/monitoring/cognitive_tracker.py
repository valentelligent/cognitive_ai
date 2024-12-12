"""
Cognitive Interaction Tracker - Extends the base interaction tracker with cognitive load metrics
"""

import time
import math
import numpy as np
from datetime import datetime, time as dt_time
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
from .interaction_tracker import InteractionTracker
from ..gpu.cuda_operations import GPUManager

class CognitiveInteractionTracker(InteractionTracker):
    def __init__(self, 
                 log_dir: str = "interaction_logs",
                 schedule: Optional[Dict[str, List[dt_time]]] = None,
                 task_types: Optional[List[str]] = None,
                 gpu_memory_limit: float = 0.8):
        """Initialize cognitive tracker with graceful fallback for GPU operations"""
        # Initialize base tracker first
        super().__init__(log_dir)
        
        try:
            self.schedule = schedule or {}  # Format: {"task_type": [start_time, end_time]}
            self.task_types = task_types or ["coding", "reading", "writing", "research"]
            self.current_task = None
            
            # Initialize cognitive metrics storage
            self.cognitive_metrics = {
                # Memory domain
                "folder_access_patterns": [],  # Track folder navigation
                "repeated_actions": defaultdict(int),  # Count repeated actions
                "save_patterns": [],  # Track file saving behavior
                
                # Executive function domain
                "task_switches": [],  # Window/application changes
                "multitasking_events": [],  # Parallel task handling
                "organization_patterns": [],  # File/folder organization
                
                # Language domain
                "typing_speed": [],  # WPM
                "error_rate": [],  # Backspace frequency
                "vocabulary_usage": defaultdict(int),  # Word frequency
                "pause_patterns": [],  # Time between keystrokes
                
                # Perception and action domain
                "mouse_precision": [],  # Mouse movement accuracy
                "click_patterns": [],  # Click accuracy and timing
                "ui_interaction_speed": [],  # Speed of UI interactions
                
                # General patterns
                "focus_duration": [],  # Time spent in each window
                "daily_usage": defaultdict(dict),  # Daily usage statistics
                "activity_complexity": []  # Complexity of performed tasks
            }
            
            # Initialize GPU manager with fallback
            self.gpu_manager = None
            try:
                self.gpu_manager = GPUManager(gpu_memory_limit)
                if self.gpu_manager.cuda_available:
                    self.logger.info("GPU acceleration enabled")
                else:
                    self.logger.info("Using CPU fallback for computations")
            except Exception as e:
                self.logger.warning(f"Failed to initialize GPU manager: {e}. Using CPU fallback.")
                
        except Exception as e:
            self.logger.error(f"Error initializing cognitive metrics: {e}")
            raise
        
        self.last_window = None
        self.last_window_time = time.time()
        self.last_mouse_position = None
        self.last_folder_access = None
        self.historical_metrics = {}  # Store historical data for trend analysis
        
    def _analyze_memory_patterns(self, events: List[Dict]) -> Dict:
        """Analyze patterns related to memory domain."""
        metrics = {
            'incorrect_folder_attempts': 0,
            'repeated_access_count': 0,
            'save_frequency': 0.0,
            'memory_score': 0.0
        }
        
        folder_sequence = []
        for event in events:
            if event['type'] == 'file_access':
                folder_sequence.append(event['path'])
                if len(folder_sequence) > 1 and folder_sequence[-1] != folder_sequence[-2]:
                    metrics['incorrect_folder_attempts'] += 1
            
        # Calculate repeated access patterns
        access_counts = defaultdict(int)
        for folder in folder_sequence:
            access_counts[folder] += 1
            if access_counts[folder] > 1:
                metrics['repeated_access_count'] += 1
        
        # Calculate memory score (0-1)
        total_actions = len(events)
        if total_actions > 0:
            error_ratio = (metrics['incorrect_folder_attempts'] + metrics['repeated_access_count']) / total_actions
            metrics['memory_score'] = max(0, 1 - error_ratio)
        
        return metrics
    
    def _analyze_executive_function(self, events: List[Dict]) -> Dict:
        """Analyze patterns related to executive function domain."""
        metrics = {
            'task_switching_frequency': 0.0,
            'multitasking_score': 0.0,
            'organization_efficiency': 0.0,
            'executive_score': 0.0
        }
        
        # Calculate task switching frequency
        window_switches = [e for e in events if e['type'] == 'window_switch']
        if len(window_switches) > 1:
            try:
                time_diff = (window_switches[-1]['timestamp'] - window_switches[0]['timestamp']).total_seconds()
                if time_diff > 0:
                    metrics['task_switching_frequency'] = len(window_switches) / (time_diff / 60)  # switches per minute
            except (KeyError, TypeError, ZeroDivisionError):
                metrics['task_switching_frequency'] = 0.0
        
        # Calculate multitasking score
        parallel_tasks = set()
        for event in events:
            if 'window_title' in event:
                parallel_tasks.add(event['window_title'])
        metrics['multitasking_score'] = min(len(parallel_tasks) / 5, 1.0)  # Normalize to 0-1
        
        # Calculate executive score
        metrics['executive_score'] = (metrics['multitasking_score'] + 
                                    (1 - min(metrics['task_switching_frequency'] / 10, 1))) / 2
        
        return metrics
    
    def _analyze_language_patterns(self, events: List[Dict]) -> Dict:
        """Analyze patterns related to language domain."""
        metrics = {
            'typing_speed': 0.0,
            'error_correction_rate': 0.0,
            'vocabulary_complexity': 0.0,
            'language_score': 0.0
        }
        
        # Calculate typing speed and error rate
        typing_events = [e for e in events if e['type'] == 'keyboard']
        if typing_events:
            try:
                time_diff = (typing_events[-1]['timestamp'] - typing_events[0]['timestamp']).total_seconds()
                char_count = len(typing_events)
                if time_diff > 0:
                    metrics['typing_speed'] = (char_count / 5) / (time_diff / 60)  # WPM
                
                error_events = len([e for e in typing_events if e['key'] == 'backspace'])
                metrics['error_correction_rate'] = error_events / char_count if char_count > 0 else 0
            except (KeyError, TypeError, ZeroDivisionError):
                metrics['typing_speed'] = 0.0
                metrics['error_correction_rate'] = 0.0
        
        # Calculate vocabulary complexity
        word_lengths = [len(word) for word in self.cognitive_metrics['vocabulary_usage'].keys()]
        if word_lengths:
            metrics['vocabulary_complexity'] = sum(word_lengths) / len(word_lengths) / 10  # Normalize to 0-1
        
        # Calculate language score
        metrics['language_score'] = (
            min(metrics['typing_speed'] / 60, 1) +  # Normalize WPM to 0-1
            (1 - metrics['error_correction_rate']) +
            metrics['vocabulary_complexity']
        ) / 3
        
        return metrics
    
    def _analyze_perception_action(self, events: List[Dict]) -> Dict:
        """Analyze patterns related to perception and action domain."""
        metrics = {
            'mouse_precision': 0.0,
            'click_accuracy': 0.0,
            'movement_smoothness': 0.0,
            'perception_score': 0.0
        }
        
        # Analyze mouse movement precision
        mouse_moves = [e for e in events if e['type'] == 'mouse' and e['event_type'] == 'move']
        if len(mouse_moves) > 1:
            distances = []
            for i in range(1, len(mouse_moves)):
                x1, y1 = mouse_moves[i-1]['position']
                x2, y2 = mouse_moves[i]['position']
                distances.append(math.sqrt((x2-x1)**2 + (y2-y1)**2))
            
            metrics['mouse_precision'] = 1 - min(np.std(distances) / 100, 1)  # Normalize to 0-1
            metrics['movement_smoothness'] = 1 - min(max(distances) / 500, 1)  # Normalize to 0-1
        
        # Analyze click accuracy
        clicks = [e for e in events if e['type'] == 'mouse' and e['event_type'] == 'click']
        if clicks and mouse_moves:
            misclicks = sum(1 for click in clicks if any(
                math.sqrt((click['position'][0]-move['position'][0])**2 + 
                         (click['position'][1]-move['position'][1])**2) > 20
                for move in mouse_moves[-5:]  # Check against last 5 moves
            ))
            metrics['click_accuracy'] = 1 - (misclicks / len(clicks))
        
        # Calculate perception score
        metrics['perception_score'] = (
            metrics['mouse_precision'] +
            metrics['click_accuracy'] +
            metrics['movement_smoothness']
        ) / 3
        
        return metrics
    
    def _analyze_usage_patterns(self, usage_data: Dict) -> Dict:
        """Analyze overall usage patterns."""
        metrics = {
            'daily_usage_variance': 0.0,
            'activity_complexity': 0.0,
            'usage_trend': 0.0
        }
        
        if usage_data:
            # Calculate daily usage variance
            durations = [data['duration'] for data in usage_data.values()]
            if durations:
                mean_duration = np.mean(durations)
                metrics['daily_usage_variance'] = np.std(durations) / mean_duration if mean_duration > 0 else 0
            
            # Calculate activity complexity
            complexity_scores = []
            for data in usage_data.values():
                score = min(data['active_windows'] / 10, 1.0)  # Normalize by max expected windows
                complexity_scores.append(score)
            metrics['activity_complexity'] = np.mean(complexity_scores) if complexity_scores else 0
            
            # Calculate usage trend (positive or negative)
            if len(durations) > 1:
                trend = np.polyfit(range(len(durations)), durations, 1)[0]
                metrics['usage_trend'] = trend / mean_duration if mean_duration > 0 else 0
        
        return metrics
    
    def _detect_behavioral_changes(self, historical: Dict, current: Dict) -> Dict:
        """Detect significant changes in behavioral metrics."""
        changes = {
            'significant_changes': [],
            'change_severity': 0.0
        }
        
        # Define significance thresholds for different metrics
        thresholds = {
            'typing_speed': 0.2,  # 20% change
            'error_rate': 0.3,    # 30% change
            'task_switching_frequency': 0.25  # 25% change
        }
        
        total_severity = 0
        for metric, threshold in thresholds.items():
            if metric in historical and metric in current:
                if historical[metric] > 0:  # Avoid division by zero
                    change = abs(current[metric] - historical[metric]) / historical[metric]
                    if change > threshold:
                        changes['significant_changes'].append({
                            'metric': metric,
                            'change': change,
                            'direction': 'increase' if current[metric] > historical[metric] else 'decrease'
                        })
                        total_severity += change
        
        if changes['significant_changes']:
            changes['change_severity'] = total_severity / len(changes['significant_changes'])
        
        return changes
    
    def _calculate_cognitive_load(self, metrics: Optional[Dict] = None) -> Dict:
        """Calculate current cognitive load based on recent interactions"""
        current_time = time.time()
        
        if metrics is None:
            metrics = {
                "typing_speed": self._calculate_typing_speed(),
                "error_rate": self._calculate_error_rate(),
                "task_switches": len(self.cognitive_metrics["task_switches"]),
                "focus_score": self._calculate_focus_score(),
            }
        
        # Calculate domain-specific scores
        domain_scores = {
            'memory': metrics.get('memory_score', 0.0),
            'executive': metrics.get('executive_score', 0.0),
            'language': metrics.get('language_score', 0.0),
            'perception': metrics.get('perception_score', 0.0)
        }
        
        # Calculate overall cognitive load score (0-1)
        overall_score = sum(domain_scores.values()) / len(domain_scores)
        
        return {
            'overall_score': overall_score,
            'domain_scores': domain_scores,
            'timestamp': current_time
        }

    def start_task(self, task_type: str):
        """Start tracking a specific task type"""
        if task_type not in self.task_types:
            raise ValueError(f"Task type must be one of {self.task_types}")
        self.current_task = task_type
        self._log_event("task_start", {"task_type": task_type})
        
    def stop_task(self):
        """Stop tracking the current task"""
        if self.current_task:
            self._log_event("task_end", {"task_type": self.current_task})
            self.current_task = None
            
    def _calculate_typing_speed(self) -> float:
        """Calculate typing speed in words per minute"""
        if not self.cognitive_metrics["typing_speed"]:
            return 0.0
        recent_speeds = self.cognitive_metrics["typing_speed"][-10:]  # Last 10 measurements
        return sum(recent_speeds) / len(recent_speeds)
        
    def _calculate_error_rate(self) -> float:
        """Calculate error rate based on backspace usage"""
        if not self.cognitive_metrics["error_rate"]:
            return 0.0
        recent_errors = self.cognitive_metrics["error_rate"][-10:]  # Last 10 measurements
        return sum(recent_errors) / len(recent_errors)
        
    def _calculate_focus_score(self) -> float:
        """Calculate focus score based on window switches and active duration"""
        if not self.cognitive_metrics["focus_duration"]:
            return 0.0
        recent_durations = self.cognitive_metrics["focus_duration"][-10:]  # Last 10 measurements
        return sum(recent_durations) / len(recent_durations)
        
    def _handle_keyboard_event(self, event):
        """Extended keyboard event handler with cognitive metrics"""
        super()._handle_keyboard_event(event)
        
        # Update cognitive metrics
        current_time = time.time()
        if event.name == "backspace":
            self.cognitive_metrics["error_rate"].append(1)
        else:
            self.cognitive_metrics["error_rate"].append(0)
            
        # Calculate typing speed
        if len(self.cognitive_metrics["pause_patterns"]) > 1:
            time_diff = current_time - self.cognitive_metrics["pause_patterns"][-1]
            if time_diff < 2.0:  # Only count if less than 2 seconds between keystrokes
                wpm = 60 / (time_diff * 5)  # Assume average word length of 5 characters
                self.cognitive_metrics["typing_speed"].append(wpm)
                
        self.cognitive_metrics["pause_patterns"].append(current_time)
        
    def _handle_window_change(self, window_info: Dict):
        """Track window changes for task switching metrics"""
        current_time = time.time()
        
        if self.last_window != window_info["window_title"]:
            if self.last_window:
                duration = current_time - self.last_window_time
                self.cognitive_metrics["focus_duration"].append(duration)
                self.cognitive_metrics["task_switches"].append({
                    "from": self.last_window,
                    "to": window_info["window_title"],
                    "time": current_time
                })
            
            self.last_window = window_info["window_title"]
            self.last_window_time = current_time
            
    def _log_event(self, event_type: str, context: Dict):
        """Extended event logging with cognitive load metrics"""
        window_info = self._get_active_window_info()
        self._handle_window_change(window_info)
        
        # Add cognitive load metrics to the event
        context.update({
            "cognitive_load": self._calculate_cognitive_load(),
            "current_task": self.current_task
        })
        
        super()._log_event(event_type, context)

if __name__ == '__main__':
    import logging
    
    # Set up logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('cognitive_tracker_debug.log')
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info("Starting cognitive tracker...")
    
    try:
        tracker = CognitiveInteractionTracker()
        logger.info("Tracker initialized successfully")
        tracker.start()
        logger.info("Tracker started successfully")
        
        while True:
            time.sleep(1)
            
    except Exception as e:
        logger.error(f"Error in cognitive tracker: {e}", exc_info=True)
        raise
