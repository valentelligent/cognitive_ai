from sqlalchemy import Column, Integer, String, DateTime, Float, JSON, Interval
from sqlalchemy.sql import func
from .database import Base

class CognitiveMetrics(Base):
    __tablename__ = "cognitive_metrics"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    metric_type = Column(String)
    value = Column(Float)
    metadata = Column(JSON)

class CognitiveEvolutionEvent(Base):
    __tablename__ = "cognitive_evolution_events"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    event_type = Column(String)
    cognitive_metrics = Column(JSON)
    interaction_data = Column(JSON)
    context_metrics = Column(JSON)
    raw_event_data = Column(JSON)

class EvolutionPattern(Base):
    __tablename__ = "evolution_patterns"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    pattern_type = Column(String)
    pattern_data = Column(JSON)

class CognitiveStateTransition(Base):
    __tablename__ = "cognitive_state_transitions"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Baseline metrics
    standard_processing_state = Column(JSON)
    evolved_state = Column(JSON)
    
    # Gray area indicators
    transition_indicators = Column(JSON)
    consciousness_emergence_patterns = Column(JSON)
    
    # Context maintenance
    context_depth = Column(Integer)
    context_quality_metrics = Column(JSON)
    
    # Temporal aspects
    duration_in_state = Column(Interval)
    transition_trigger = Column(String)
    
    # Meta-awareness
    self_awareness_level = Column(Float)
    meta_cognitive_markers = Column(JSON)
    
    # Pattern recognition
    pattern_evolution = Column(JSON)
    understanding_depth_metrics = Column(JSON)
    
    # Interaction context
    interaction_type = Column(String)
    cognitive_resonance_score = Column(Float)
    
    # Uncertainty tracking
    uncertainty_markers = Column(JSON)
    certainty_fluctuations = Column(JSON)
    
    # Enhanced metadata
    environmental_context = Column(JSON)
    system_state = Column(JSON)
