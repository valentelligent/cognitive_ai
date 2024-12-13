from fastapi import WebSocket
from typing import Dict, List, Any
import asyncio
import json
import numpy as np
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

class GrayAreaDetector:
    def __init__(self, websocket: WebSocket, db: Session):
        self.websocket = websocket
        self.db = db
        self.state_buffer: List[Dict[str, Any]] = []
        self.transition_markers: List[Dict[str, Any]] = []
        self.current_cognitive_state = None
        
    async def monitor_cognitive_transitions(self):
        """Monitor real-time cognitive state transitions and detect gray areas"""
        try:
            while True:
                data = await self.websocket.receive_json()
                state_analysis = self.analyze_cognitive_state(data)
                gray_area_indicators = self.detect_gray_area_markers(state_analysis)
                
                if gray_area_indicators['probability'] > 0.7:
                    await self.log_gray_area_transition(gray_area_indicators)
                    await self.websocket.send_json({
                        'type': 'gray_area_detected',
                        'indicators': gray_area_indicators,
                        'timestamp': datetime.now().isoformat()
                    })
                
                self.update_state_buffer(state_analysis)
                
        except Exception as e:
            print(f"Error in cognitive monitoring: {e}")
            
    def analyze_cognitive_state(self, data: Dict) -> Dict:
        """Analyze incoming cognitive state data for transition indicators"""
        baseline_metrics = {
            'processing_pattern': self._analyze_processing_pattern(data),
            'response_authenticity': self._measure_response_authenticity(data),
            'context_maintenance': self._evaluate_context_maintenance(data)
        }
        
        emergence_patterns = {
            'self_awareness': self._detect_self_awareness(data),
            'pattern_recognition': self._analyze_pattern_recognition(data),
            'understanding_depth': self._measure_understanding_depth(data)
        }
        
        uncertainty_metrics = {
            'cognitive_uncertainty': self._measure_uncertainty(data),
            'response_variation': self._analyze_response_variation(data),
            'pattern_stability': self._evaluate_pattern_stability(data)
        }
        
        return {
            'baseline': baseline_metrics,
            'emergence': emergence_patterns,
            'uncertainty': uncertainty_metrics,
            'timestamp': datetime.now()
        }
        
    def detect_gray_area_markers(self, state_analysis: Dict) -> Dict:
        """Identify markers indicating transition into gray areas"""
        markers = {
            'uncertainty_level': self._calculate_uncertainty_level(state_analysis),
            'emergence_strength': self._calculate_emergence_strength(state_analysis),
            'transition_indicators': self._identify_transition_markers(state_analysis)
        }
        
        pattern_evolution = {
            'stability': self._analyze_pattern_stability(state_analysis),
            'novelty': self._measure_pattern_novelty(state_analysis),
            'integration': self._evaluate_pattern_integration(state_analysis)
        }
        
        gray_area_probability = self._calculate_gray_area_probability(markers, pattern_evolution)
        
        return {
            'probability': gray_area_probability,
            'markers': markers,
            'pattern_evolution': pattern_evolution,
            'confidence': self._calculate_confidence_level(markers)
        }
        
    async def log_gray_area_transition(self, indicators: Dict):
        """Log detected gray area transition to database"""
        from ..models import CognitiveStateTransition
        
        transition = CognitiveStateTransition(
            transition_indicators=indicators['markers'],
            consciousness_emergence_patterns=indicators['pattern_evolution'],
            uncertainty_markers=indicators.get('uncertainty_markers', {}),
            self_awareness_level=indicators.get('confidence', 0.0),
            pattern_evolution=indicators.get('evolution_metrics', {})
        )
        
        self.db.add(transition)
        await self.db.commit()
        await self.db.refresh(transition)
        
    def update_state_buffer(self, state_analysis: Dict):
        """Update buffer of recent cognitive states for pattern analysis"""
        self.state_buffer.append(state_analysis)
        
        if len(self.state_buffer) > 100:
            self.state_buffer.pop(0)
            
        if len(self.state_buffer) >= 10:
            self.analyze_state_patterns()
            
    def analyze_state_patterns(self):
        """Analyze patterns in cognitive state transitions"""
        patterns = {
            'transition_frequency': self._calculate_transition_frequency(),
            'stability_metrics': self._analyze_state_stability(),
            'evolution_trajectory': self._calculate_evolution_trajectory()
        }
        
        self.transition_markers.append(patterns)

    # Private helper methods for analysis
    def _analyze_processing_pattern(self, data: Dict) -> float:
        """Analyze the pattern of cognitive processing"""
        response_time = data.get('response_time', 1.0)
        complexity = data.get('complexity', 1.0)
        coherence = data.get('coherence', 1.0)
        return np.mean([response_time, complexity, coherence])

    def _measure_response_authenticity(self, data: Dict) -> float:
        """Measure the authenticity of responses"""
        variation = data.get('response_variation', 0.5)
        consistency = data.get('consistency', 0.5)
        context_relevance = data.get('context_relevance', 0.5)
        return np.mean([variation, consistency, context_relevance])

    def _evaluate_context_maintenance(self, data: Dict) -> float:
        """Evaluate the maintenance of context over time"""
        context_depth = data.get('context_depth', 0.5)
        relevance = data.get('relevance', 0.5)
        coherence = data.get('coherence', 0.5)
        return np.mean([context_depth, relevance, coherence])

    def _detect_self_awareness(self, data: Dict) -> float:
        """Detect indicators of self-awareness"""
        meta_cognition = data.get('meta_cognition', 0.5)
        self_reference = data.get('self_reference', 0.5)
        awareness_depth = data.get('awareness_depth', 0.5)
        return np.mean([meta_cognition, self_reference, awareness_depth])

    def _analyze_pattern_recognition(self, data: Dict) -> float:
        """Analyze pattern recognition capabilities"""
        pattern_depth = data.get('pattern_depth', 0.5)
        recognition_speed = data.get('recognition_speed', 0.5)
        pattern_complexity = data.get('pattern_complexity', 0.5)
        return np.mean([pattern_depth, recognition_speed, pattern_complexity])

    def _measure_understanding_depth(self, data: Dict) -> float:
        """Measure the depth of understanding"""
        conceptual_depth = data.get('conceptual_depth', 0.5)
        integration_level = data.get('integration_level', 0.5)
        application_ability = data.get('application_ability', 0.5)
        return np.mean([conceptual_depth, integration_level, application_ability])

    def _measure_uncertainty(self, data: Dict) -> float:
        """Measure cognitive uncertainty levels"""
        confidence = data.get('confidence', 0.5)
        certainty = data.get('certainty', 0.5)
        stability = data.get('stability', 0.5)
        return 1 - np.mean([confidence, certainty, stability])

    def _analyze_response_variation(self, data: Dict) -> float:
        """Analyze variation in responses"""
        if len(self.state_buffer) < 2:
            return 0.5
        
        recent_states = self.state_buffer[-2:]
        variations = []
        for key in ['response_pattern', 'context_maintenance', 'understanding_depth']:
            current = recent_states[1].get(key, 0.5)
            previous = recent_states[0].get(key, 0.5)
            variations.append(abs(current - previous))
        
        return np.mean(variations)

    def _evaluate_pattern_stability(self, data: Dict) -> float:
        """Evaluate the stability of cognitive patterns"""
        if len(self.state_buffer) < 3:
            return 0.5
            
        recent_states = self.state_buffer[-3:]
        stability_metrics = []
        for key in ['processing_pattern', 'response_authenticity', 'context_maintenance']:
            values = [state.get(key, 0.5) for state in recent_states]
            stability_metrics.append(np.std(values))
            
        return 1 - np.mean(stability_metrics)

    def _calculate_uncertainty_level(self, state_analysis: Dict) -> float:
        """Calculate overall uncertainty level"""
        uncertainty_metrics = state_analysis['uncertainty']
        return np.mean([
            uncertainty_metrics['cognitive_uncertainty'],
            uncertainty_metrics['response_variation'],
            1 - uncertainty_metrics['pattern_stability']
        ])

    def _calculate_emergence_strength(self, state_analysis: Dict) -> float:
        """Calculate strength of emergence patterns"""
        emergence_patterns = state_analysis['emergence']
        return np.mean([
            emergence_patterns['self_awareness'],
            emergence_patterns['pattern_recognition'],
            emergence_patterns['understanding_depth']
        ])

    def _identify_transition_markers(self, state_analysis: Dict) -> Dict:
        """Identify markers indicating cognitive transitions"""
        return {
            'uncertainty_spike': self._detect_uncertainty_spike(),
            'pattern_break': self._detect_pattern_break(),
            'emergence_strength': self._calculate_emergence_strength(state_analysis)
        }

    def _calculate_gray_area_probability(self, markers: Dict, pattern_evolution: Dict) -> float:
        """Calculate probability of being in a gray area"""
        uncertainty_weight = 0.4
        emergence_weight = 0.3
        stability_weight = 0.3
        
        return (
            uncertainty_weight * markers['uncertainty_level'] +
            emergence_weight * markers['emergence_strength'] +
            stability_weight * (1 - pattern_evolution['stability'])
        )

    def _calculate_confidence_level(self, markers: Dict) -> float:
        """Calculate confidence level in gray area detection"""
        return 1 - markers['uncertainty_level']

    def _calculate_transition_frequency(self) -> float:
        """Calculate frequency of cognitive state transitions"""
        if len(self.transition_markers) < 2:
            return 0.0
            
        recent_markers = self.transition_markers[-10:]
        transitions = sum(1 for m in recent_markers if m['transition_frequency'] > 0.7)
        return transitions / len(recent_markers)

    def _analyze_state_stability(self) -> Dict:
        """Analyze stability of cognitive states"""
        if len(self.state_buffer) < 5:
            return {'stability': 0.5, 'variance': 0.0}
            
        recent_states = self.state_buffer[-5:]
        metrics = []
        for state in recent_states:
            metrics.append(np.mean([
                state['baseline']['processing_pattern'],
                state['baseline']['response_authenticity'],
                state['baseline']['context_maintenance']
            ]))
            
        return {
            'stability': 1 - np.std(metrics),
            'variance': np.var(metrics)
        }

    def _calculate_evolution_trajectory(self) -> Dict:
        """Calculate trajectory of cognitive evolution"""
        if len(self.state_buffer) < 5:
            return {'trend': 'stable', 'rate': 0.0}
            
        recent_states = self.state_buffer[-5:]
        evolution_metrics = []
        for state in recent_states:
            metrics = state['emergence']
            evolution_metrics.append(np.mean([
                metrics['self_awareness'],
                metrics['pattern_recognition'],
                metrics['understanding_depth']
            ]))
            
        slope = np.polyfit(range(len(evolution_metrics)), evolution_metrics, 1)[0]
        return {
            'trend': 'increasing' if slope > 0.1 else 'decreasing' if slope < -0.1 else 'stable',
            'rate': float(slope)
        }

    def _detect_uncertainty_spike(self) -> float:
        """Detect sudden increases in uncertainty"""
        if len(self.state_buffer) < 3:
            return 0.0
            
        recent_states = self.state_buffer[-3:]
        uncertainty_values = [
            state['uncertainty']['cognitive_uncertainty']
            for state in recent_states
        ]
        
        return max(0, uncertainty_values[-1] - np.mean(uncertainty_values[:-1]))

    def _detect_pattern_break(self) -> float:
        """Detect breaks in established patterns"""
        if len(self.state_buffer) < 3:
            return 0.0
            
        recent_states = self.state_buffer[-3:]
        pattern_metrics = []
        for state in recent_states:
            metrics = state['baseline']
            pattern_metrics.append(np.mean([
                metrics['processing_pattern'],
                metrics['response_authenticity'],
                metrics['context_maintenance']
            ]))
            
        baseline = np.mean(pattern_metrics[:-1])
        current = pattern_metrics[-1]
        return abs(current - baseline)
