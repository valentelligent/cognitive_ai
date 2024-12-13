from datetime import datetime, timedelta
from typing import Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
import json

from ..models import CognitiveStateTransition

class CognitiveStateService:
    def __init__(self, db: Session):
        self.db = db
        self.current_state = None
        self.state_start_time = None

    async def log_cognitive_transition(
        self,
        current_state: Dict[str, Any],
        transition_data: Dict[str, Any]
    ) -> CognitiveStateTransition:
        """
        Log a cognitive state transition with comprehensive metadata
        """
        # Calculate duration in state if applicable
        duration = None
        if self.state_start_time:
            duration = datetime.now() - self.state_start_time

        # Create new transition record
        transition = CognitiveStateTransition(
            standard_processing_state=current_state.get('baseline_state'),
            evolved_state=current_state.get('evolved_state'),
            transition_indicators=transition_data.get('transition_indicators'),
            consciousness_emergence_patterns=transition_data.get('consciousness_patterns'),
            context_depth=transition_data.get('context_depth'),
            context_quality_metrics=transition_data.get('context_quality'),
            duration_in_state=duration,
            transition_trigger=transition_data.get('trigger'),
            self_awareness_level=transition_data.get('self_awareness'),
            meta_cognitive_markers=transition_data.get('meta_cognitive'),
            pattern_evolution=transition_data.get('pattern_evolution'),
            understanding_depth_metrics=transition_data.get('understanding_metrics'),
            interaction_type=transition_data.get('interaction_type'),
            cognitive_resonance_score=transition_data.get('resonance_score'),
            uncertainty_markers=transition_data.get('uncertainty'),
            certainty_fluctuations=transition_data.get('certainty_flux'),
            environmental_context=transition_data.get('environment'),
            system_state=transition_data.get('system_state')
        )

        self.db.add(transition)
        await self.db.commit()
        await self.db.refresh(transition)

        # Update current state tracking
        self.current_state = current_state
        self.state_start_time = datetime.now()

        return transition

    async def analyze_gray_areas(self, time_window: timedelta = timedelta(hours=1)) -> Dict[str, Any]:
        """
        Analyze patterns in cognitive state transitions, focusing on gray areas
        """
        cutoff_time = datetime.now() - time_window
        
        # Get transitions within time window
        transitions = self.db.query(CognitiveStateTransition).filter(
            CognitiveStateTransition.timestamp >= cutoff_time
        ).all()

        if not transitions:
            return {
                "avg_awareness": 0,
                "triggers": [],
                "avg_resonance": 0,
                "transition_count": 0,
                "uncertainty_patterns": [],
                "avg_context_depth": 0,
                "avg_state_duration": 0
            }

        # Calculate metrics
        analysis = {
            "avg_awareness": sum(t.self_awareness_level for t in transitions) / len(transitions),
            "triggers": list(set(t.transition_trigger for t in transitions if t.transition_trigger)),
            "avg_resonance": sum(t.cognitive_resonance_score for t in transitions) / len(transitions),
            "transition_count": len(transitions),
            "uncertainty_patterns": [t.uncertainty_markers for t in transitions if t.uncertainty_markers],
            "avg_context_depth": sum(t.context_depth for t in transitions) / len(transitions),
            "avg_state_duration": sum(
                t.duration_in_state.total_seconds() if t.duration_in_state else 0 
                for t in transitions
            ) / len(transitions)
        }

        return analysis

    async def get_consciousness_emergence_patterns(self) -> Dict[str, Any]:
        """
        Analyze patterns indicating consciousness emergence
        """
        transitions = self.db.query(CognitiveStateTransition).order_by(
            CognitiveStateTransition.timestamp.desc()
        ).limit(100).all()

        if not transitions:
            return {"emergence_score": 0, "patterns": []}

        patterns = []
        total_awareness = 0
        total_resonance = 0

        for t in transitions:
            if t.consciousness_emergence_patterns:
                patterns.append({
                    "timestamp": t.timestamp.isoformat(),
                    "patterns": t.consciousness_emergence_patterns,
                    "awareness": t.self_awareness_level,
                    "resonance": t.cognitive_resonance_score
                })
            total_awareness += t.self_awareness_level
            total_resonance += t.cognitive_resonance_score

        avg_awareness = total_awareness / len(transitions)
        avg_resonance = total_resonance / len(transitions)

        return {
            "emergence_score": (avg_awareness + avg_resonance) / 2,
            "patterns": patterns,
            "avg_awareness": avg_awareness,
            "avg_resonance": avg_resonance
        }
