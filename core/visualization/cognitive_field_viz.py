"""
Cognitive Field Visualization System
Implements real-time visualization of cognitive patterns and resonances.
"""

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import List, Dict, Optional
import pandas as pd
from datetime import datetime, timedelta
from ..analysis.cognitive_patterns import CognitivePattern, TimeScale
from ..analysis.cognitive_resonance import CognitiveResonance, ResonanceType

class CognitiveFieldVisualizer:
    def __init__(self):
        self.fig = None
        self.last_update = datetime.now()
        self.development_metrics = {
            'coding_sessions': [],
            'learning_moments': [],
            'task_switches': [],
            'cognitive_load_history': []
        }
        self._setup_figure()
        
    def _setup_figure(self):
        """Initialize the visualization figure"""
        self.fig = make_subplots(
            rows=4, cols=2,
            subplot_titles=(
                'Cognitive Load & Focus',
                'Pattern Distribution',
                'Resonance Strength',
                'Emergence Potential',
                'Learning Trajectory',
                'Cognitive Field',
                'Development Progress',
                'Learning Moments'
            ),
            specs=[
                [{"type": "scatter"}, {"type": "pie"}],
                [{"type": "scatter"}, {"type": "heatmap"}],
                [{"type": "scatter3d"}, {"type": "scatter"}],
                [{"type": "scatter"}, {"type": "scatter"}]
            ]
        )
        
        self.fig.update_layout(
            height=1200,
            showlegend=True,
            title_text="Cognitive Field Analysis & Development Tracking",
            title_x=0.5
        )
        
    def update_visualization(self, 
                           patterns: List[CognitivePattern],
                           resonances: List[CognitiveResonance]):
        """Update the visualization with new patterns and resonances"""
        if not patterns:
            return
            
        self._update_cognitive_load(patterns)
        self._update_pattern_distribution(patterns)
        self._update_resonance_strength(resonances)
        self._update_emergence_potential(patterns)
        self._update_learning_trajectory(patterns, resonances)
        self._update_cognitive_field(patterns, resonances)
        self._update_development_progress()
        self._visualize_learning_moments()
        
        self.last_update = datetime.now()
        
    def _update_cognitive_load(self, patterns: List[CognitivePattern]):
        """Update cognitive load visualization"""
        times = [datetime.fromtimestamp(p.start_time) for p in patterns]
        loads = [p.metrics.get('cognitive_load', 0) for p in patterns]
        focus = [p.metrics.get('avg_focus_duration', 0) for p in patterns]
        
        self.fig.add_trace(
            go.Scatter(
                x=times,
                y=loads,
                name='Cognitive Load',
                line=dict(color='blue'),
                showlegend=True
            ),
            row=1, col=1
        )
        
        self.fig.add_trace(
            go.Scatter(
                x=times,
                y=focus,
                name='Focus Duration',
                line=dict(color='red'),
                showlegend=True
            ),
            row=1, col=1
        )
        
    def _update_pattern_distribution(self, patterns: List[CognitivePattern]):
        """Update pattern distribution visualization"""
        pattern_counts = {}
        for pattern in patterns:
            pattern_counts[pattern.pattern_type] = pattern_counts.get(pattern.pattern_type, 0) + 1
            
        self.fig.add_trace(
            go.Pie(
                labels=list(pattern_counts.keys()),
                values=list(pattern_counts.values()),
                name='Pattern Distribution'
            ),
            row=1, col=2
        )
        
    def _update_resonance_strength(self, resonances: List[CognitiveResonance]):
        """Update resonance strength visualization"""
        times = [datetime.fromtimestamp(r.patterns[0].start_time) for r in resonances]
        strengths = [r.strength for r in resonances]
        types = [r.type.value for r in resonances]
        
        self.fig.add_trace(
            go.Scatter(
                x=times,
                y=strengths,
                mode='markers',
                marker=dict(
                    size=10,
                    color=[self._get_resonance_color(t) for t in types],
                    symbol=[self._get_resonance_symbol(t) for t in types]
                ),
                name='Resonance Strength'
            ),
            row=2, col=1
        )
        
    def _update_emergence_potential(self, patterns: List[CognitivePattern]):
        """Update emergence potential visualization"""
        times = np.array([p.start_time for p in patterns])
        loads = np.array([p.metrics.get('cognitive_load', 0) for p in patterns])
        focus = np.array([p.metrics.get('avg_focus_duration', 0) for p in patterns])
        
        # Create emergence potential heatmap
        heatmap = np.outer(loads, focus)
        
        self.fig.add_trace(
            go.Heatmap(
                z=heatmap,
                colorscale='Viridis',
                name='Emergence Potential'
            ),
            row=2, col=2
        )
        
    def _update_learning_trajectory(self, 
                                  patterns: List[CognitivePattern],
                                  resonances: List[CognitiveResonance]):
        """Update learning trajectory visualization"""
        if not patterns or not resonances:
            return
            
        # Create 3D learning trajectory
        times = np.array([p.start_time for p in patterns])
        loads = np.array([p.metrics.get('cognitive_load', 0) for p in patterns])
        focus = np.array([p.metrics.get('avg_focus_duration', 0) for p in patterns])
        emergence = np.array([p.metrics.get('emergence_potential', 0) 
                            for p in patterns])
        
        self.fig.add_trace(
            go.Scatter3d(
                x=times,
                y=loads,
                z=focus,
                mode='lines+markers',
                marker=dict(
                    size=5,
                    color=emergence,
                    colorscale='Viridis',
                    showscale=True
                ),
                name='Learning Trajectory'
            ),
            row=3, col=1
        )
        
    def _update_cognitive_field(self, 
                              patterns: List[CognitivePattern],
                              resonances: List[CognitiveResonance]):
        """Update cognitive field visualization"""
        # Create field strength visualization
        times = np.array([p.start_time for p in patterns])
        field_strength = self._calculate_field_strength(patterns, resonances)
        
        self.fig.add_trace(
            go.Scatter(
                x=[datetime.fromtimestamp(t) for t in times],
                y=field_strength,
                fill='tozeroy',
                name='Cognitive Field'
            ),
            row=3, col=2
        )
        
    def _calculate_field_strength(self, 
                                patterns: List[CognitivePattern],
                                resonances: List[CognitiveResonance]) -> np.ndarray:
        """Calculate cognitive field strength"""
        if not patterns:
            return np.array([])
            
        times = np.array([p.start_time for p in patterns])
        base_strength = np.array([p.metrics.get('cognitive_load', 0) * 
                                p.metrics.get('avg_focus_duration', 0)
                                for p in patterns])
                                
        # Add resonance effects
        for resonance in resonances:
            res_time = resonance.patterns[0].start_time
            # Calculate gaussian influence of resonance
            influence = resonance.strength * np.exp(-0.5 * 
                ((times - res_time) / (60 * 60)) ** 2)  # 1-hour standard deviation
            base_strength += influence
            
        return base_strength
        
    def _get_resonance_color(self, resonance_type: str) -> str:
        """Get color for resonance type"""
        colors = {
            'learning': 'blue',
            'insight': 'green',
            'integration': 'purple',
            'innovation': 'red'
        }
        return colors.get(resonance_type, 'gray')
        
    def _get_resonance_symbol(self, resonance_type: str) -> str:
        """Get symbol for resonance type"""
        symbols = {
            'learning': 'circle',
            'insight': 'star',
            'integration': 'diamond',
            'innovation': 'cross'
        }
        return symbols.get(resonance_type, 'circle')
        
    def track_development_session(self, session_data: Dict):
        """Track metrics from the current development session"""
        self.development_metrics['coding_sessions'].append({
            'timestamp': datetime.now(),
            'duration': session_data.get('duration'),
            'lines_changed': session_data.get('lines_changed'),
            'files_modified': session_data.get('files_modified'),
            'cognitive_load': session_data.get('cognitive_load')
        })
        
        if session_data.get('learning_moments'):
            self.development_metrics['learning_moments'].extend(session_data['learning_moments'])
            
        self.development_metrics['cognitive_load_history'].append({
            'timestamp': datetime.now(),
            'load': session_data.get('cognitive_load'),
            'context': session_data.get('current_task')
        })
        
    def _update_development_progress(self):
        """Visualize development progress metrics"""
        sessions = self.development_metrics['coding_sessions']
        if not sessions:
            return
            
        times = [s['timestamp'] for s in sessions]
        productivity = [s['lines_changed'] / s['duration'].total_seconds() for s in sessions]
        cognitive_load = [s['cognitive_load'] for s in sessions]
        
        # Plot productivity over time
        self.fig.add_trace(
            go.Scatter(
                x=times,
                y=productivity,
                name='Development Productivity',
                line=dict(color='green'),
                showlegend=True
            ),
            row=4, col=1
        )
        
        # Plot cognitive load during development
        self.fig.add_trace(
            go.Scatter(
                x=times,
                y=cognitive_load,
                name='Development Cognitive Load',
                line=dict(color='orange'),
                showlegend=True
            ),
            row=4, col=1
        )
        
    def _visualize_learning_moments(self):
        """Visualize learning moments during development"""
        moments = self.development_metrics['learning_moments']
        if not moments:
            return
            
        times = [m['timestamp'] for m in moments]
        types = [m['type'] for m in moments]
        significance = [m['significance'] for m in moments]
        
        # Create scatter plot of learning moments
        self.fig.add_trace(
            go.Scatter(
                x=times,
                y=significance,
                mode='markers',
                marker=dict(
                    size=10,
                    color=significance,
                    colorscale='Viridis',
                    showscale=True
                ),
                text=types,
                name='Learning Moments'
            ),
            row=4, col=2
        )
        
    def save_visualization(self, filename: str):
        """Save current visualization to file"""
        if self.fig:
            self.fig.write_html(filename)
            
    def display(self):
        """Display the visualization"""
        if self.fig:
            self.fig.show()
