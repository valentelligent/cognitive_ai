"""
Development Process Tracker
Tracks and analyzes the development process of the cognitive AI system itself
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import numpy as np

@dataclass
class DevelopmentEvent:
    timestamp: datetime
    event_type: str  # 'code_change', 'learning_moment', 'task_switch', etc.
    details: Dict
    cognitive_load: float
    files_affected: List[str]
    
@dataclass
class LearningMoment:
    timestamp: datetime
    type: str  # 'insight', 'error_recovery', 'concept_mastery'
    description: str
    significance: float
    context: Dict
    
class DevelopmentTracker:
    def __init__(self):
        self.events: List[DevelopmentEvent] = []
        self.learning_moments: List[LearningMoment] = []
        self.session_start = datetime.now()
        self.current_cognitive_load = 0.0
        self.files_in_context = set()
        
    def track_event(self, event_type: str, details: Dict, files: List[str]):
        """Track a development event"""
        event = DevelopmentEvent(
            timestamp=datetime.now(),
            event_type=event_type,
            details=details,
            cognitive_load=self.current_cognitive_load,
            files_affected=files
        )
        self.events.append(event)
        self.files_in_context.update(files)
        
    def record_learning_moment(self, 
                             moment_type: str,
                             description: str,
                             significance: float,
                             context: Dict):
        """Record a learning moment during development"""
        moment = LearningMoment(
            timestamp=datetime.now(),
            type=moment_type,
            description=description,
            significance=significance,
            context=context
        )
        self.learning_moments.append(moment)
        
    def update_cognitive_load(self, load: float):
        """Update the current cognitive load estimate"""
        self.current_cognitive_load = load
        
    def get_session_metrics(self) -> Dict:
        """Get metrics for the current development session"""
        current_time = datetime.now()
        session_duration = current_time - self.session_start
        
        # Calculate various metrics
        events_by_type = {}
        for event in self.events:
            events_by_type[event.event_type] = events_by_type.get(event.event_type, 0) + 1
            
        # Calculate average cognitive load
        avg_load = np.mean([event.cognitive_load for event in self.events]) if self.events else 0
        
        # Identify learning patterns
        learning_patterns = self._analyze_learning_patterns()
        
        return {
            'duration': session_duration,
            'event_counts': events_by_type,
            'files_modified': len(self.files_in_context),
            'avg_cognitive_load': avg_load,
            'learning_moments': len(self.learning_moments),
            'learning_patterns': learning_patterns
        }
        
    def _analyze_learning_patterns(self) -> List[Dict]:
        """Analyze patterns in learning moments"""
        if not self.learning_moments:
            return []
            
        patterns = []
        moment_types = set(m.type for m in self.learning_moments)
        
        for type_ in moment_types:
            type_moments = [m for m in self.learning_moments if m.type == type_]
            avg_significance = np.mean([m.significance for m in type_moments])
            
            patterns.append({
                'type': type_,
                'frequency': len(type_moments),
                'avg_significance': avg_significance,
                'examples': [m.description for m in type_moments[:3]]  # Top 3 examples
            })
            
        return patterns
        
    def get_development_timeline(self) -> List[Dict]:
        """Get a timeline of development events and learning moments"""
        timeline = []
        
        # Combine events and learning moments
        for event in self.events:
            timeline.append({
                'timestamp': event.timestamp,
                'type': 'development_event',
                'details': event.details,
                'cognitive_load': event.cognitive_load
            })
            
        for moment in self.learning_moments:
            timeline.append({
                'timestamp': moment.timestamp,
                'type': 'learning_moment',
                'details': {
                    'type': moment.type,
                    'description': moment.description,
                    'significance': moment.significance
                }
            })
            
        # Sort by timestamp
        timeline.sort(key=lambda x: x['timestamp'])
        return timeline
