"""
Cognitive Field System
Integrates pattern detection, resonance analysis, and visualization components.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json
import asyncio
from .analysis.cognitive_patterns import (
    CognitivePatternAnalyzer,
    CognitivePattern,
    TimeScale
)
from .analysis.cognitive_resonance import (
    CognitiveFieldAnalyzer,
    CognitiveResonance,
    ResonanceType
)
from .visualization.cognitive_field_viz import CognitiveFieldVisualizer
from .analysis.development_tracker import DevelopmentTracker
from .validation.metric_validator import MetricValidator
from .context.browser_context import BrowserContextAnalyzer
import pandas as pd

class CognitiveFieldSystem:
    def __init__(self, log_dir: str = "interaction_logs"):
        self.logger = logging.getLogger(__name__)
        self.log_dir = Path(log_dir)
        
        # Initialize components
        self.pattern_analyzer = CognitivePatternAnalyzer(log_dir)
        self.field_analyzer = CognitiveFieldAnalyzer()
        self.visualizer = CognitiveFieldVisualizer()
        self.development_tracker = DevelopmentTracker()
        self.metric_validator = MetricValidator()
        self.context_analyzer = BrowserContextAnalyzer()
        
        # State tracking
        self.patterns: Dict[TimeScale, List[CognitivePattern]] = {
            TimeScale.MICRO: [],
            TimeScale.MESO: [],
            TimeScale.MACRO: []
        }
        self.resonances: List[CognitiveResonance] = []
        self.last_update = datetime.now()
        self.validation_interval = timedelta(minutes=30)
        self.last_validation = None
        
    async def start(self):
        """Start the cognitive field system"""
        self.logger.info("Starting Cognitive Field System...")
        
        try:
            # Start analysis loops
            await asyncio.gather(
                self._run_micro_analysis(),
                self._run_meso_analysis(),
                self._run_macro_analysis(),
                self._run_visualization(),
                self._run_development_tracking(),
                self._run_validation_loop()
            )
        except Exception as e:
            self.logger.error(f"Error in Cognitive Field System: {e}")
            raise
            
    async def _run_micro_analysis(self):
        """Run micro-scale pattern analysis"""
        while True:
            try:
                # Read recent events
                events = self._read_recent_events(timedelta(minutes=5))
                
                # Analyze patterns
                micro_patterns = self.pattern_analyzer.analyze_micro_patterns(events)
                self.patterns[TimeScale.MICRO].extend(micro_patterns)
                
                # Detect resonances
                if micro_patterns:
                    resonance = self.field_analyzer.detect_resonance(micro_patterns)
                    if resonance:
                        self.resonances.append(resonance)
                        self._log_resonance(resonance)
                        
                # Prune old patterns
                self._prune_patterns(TimeScale.MICRO, timedelta(minutes=30))
                
            except Exception as e:
                self.logger.error(f"Error in micro analysis: {e}")
                
            await asyncio.sleep(1)  # Run every second
            
    async def _run_meso_analysis(self):
        """Run meso-scale pattern analysis"""
        while True:
            try:
                # Analyze patterns
                meso_patterns = self.pattern_analyzer.analyze_meso_patterns(
                    self.patterns[TimeScale.MICRO]
                )
                self.patterns[TimeScale.MESO].extend(meso_patterns)
                
                # Detect resonances
                if meso_patterns:
                    resonance = self.field_analyzer.detect_resonance(meso_patterns)
                    if resonance:
                        self.resonances.append(resonance)
                        self._log_resonance(resonance)
                        
                # Prune old patterns
                self._prune_patterns(TimeScale.MESO, timedelta(hours=4))
                
            except Exception as e:
                self.logger.error(f"Error in meso analysis: {e}")
                
            await asyncio.sleep(60)  # Run every minute
            
    async def _run_macro_analysis(self):
        """Run macro-scale pattern analysis"""
        while True:
            try:
                # Analyze patterns
                macro_patterns = self.pattern_analyzer.analyze_macro_patterns(
                    self.patterns[TimeScale.MESO]
                )
                self.patterns[TimeScale.MACRO].extend(macro_patterns)
                
                # Detect resonances
                if macro_patterns:
                    resonance = self.field_analyzer.detect_resonance(macro_patterns)
                    if resonance:
                        self.resonances.append(resonance)
                        self._log_resonance(resonance)
                        
                # Prune old patterns
                self._prune_patterns(TimeScale.MACRO, timedelta(days=7))
                
            except Exception as e:
                self.logger.error(f"Error in macro analysis: {e}")
                
            await asyncio.sleep(300)  # Run every 5 minutes
            
    async def _run_visualization(self):
        """Run visualization updates"""
        while True:
            try:
                # Update visualization
                self.visualizer.update_visualization(
                    self._get_all_patterns(),
                    self.resonances
                )
                
                # Save visualization
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                self.visualizer.save_visualization(
                    f"visualization/cognitive_field_{timestamp}.html"
                )
                
            except Exception as e:
                self.logger.error(f"Error in visualization: {e}")
                
            await asyncio.sleep(5)  # Update every 5 seconds
            
    async def _run_development_tracking(self):
        """Run development process tracking"""
        while True:
            try:
                # Get current session metrics
                session_metrics = self.development_tracker.get_session_metrics()
                
                # Update cognitive load based on current patterns
                if self.patterns[TimeScale.MICRO]:
                    current_load = self.patterns[TimeScale.MICRO][-1].metrics.get('cognitive_load', 0)
                    self.development_tracker.update_cognitive_load(current_load)
                
                # Detect learning moments from resonances
                for resonance in self.resonances:
                    if resonance.type in [ResonanceType.INSIGHT, ResonanceType.INTEGRATION]:
                        self.development_tracker.record_learning_moment(
                            moment_type=resonance.type.name.lower(),
                            description=resonance.description,
                            significance=resonance.strength,
                            context={
                                'patterns': [p.pattern_type for p in resonance.patterns],
                                'cognitive_load': resonance.metrics.get('cognitive_load', 0)
                            }
                        )
                
                # Update visualization with development metrics
                self.visualizer.track_development_session({
                    'duration': session_metrics['duration'],
                    'lines_changed': len(self.patterns[TimeScale.MICRO]),
                    'files_modified': session_metrics['files_modified'],
                    'cognitive_load': session_metrics['avg_cognitive_load'],
                    'learning_moments': [{
                        'timestamp': m.timestamp,
                        'type': m.type,
                        'significance': m.significance
                    } for m in self.development_tracker.learning_moments]
                })
                
            except Exception as e:
                self.logger.error(f"Error in development tracking: {e}")
                
            await asyncio.sleep(5)  # Update every 5 seconds
            
    async def _run_validation_loop(self):
        """Run periodic validation of cognitive metrics"""
        while True:
            try:
                current_time = datetime.now()
                
                # Run validation every 30 minutes
                if (not self.last_validation or 
                    current_time - self.last_validation >= self.validation_interval):
                    
                    # Prepare metrics data
                    metrics_data = self._prepare_metrics_for_validation()
                    
                    # Get browser context
                    browser_context = await self.context_analyzer.analyze_context(
                        current_time,
                        timedelta(minutes=30)
                    )
                    
                    # Run validation
                    validation_result = self.metric_validator.validate_cognitive_metrics(
                        metrics_data,
                        external_validations={
                            'browser_context': browser_context
                        } if browser_context else None
                    )
                    
                    # Update visualization with validation results
                    self.visualizer.update_validation_status(validation_result)
                    
                    self.last_validation = current_time
                    self.logger.info(f"Metrics validation complete: {validation_result['validation_status']}")
                    
            except Exception as e:
                self.logger.error(f"Error in validation loop: {e}")
                
            await asyncio.sleep(60)  # Check every minute
            
    def _read_recent_events(self, timeframe: timedelta) -> List[Dict]:
        """Read recent events from log files"""
        events = []
        cutoff_time = datetime.now() - timeframe
        
        # Read all log files in the directory
        for log_file in sorted(self.log_dir.glob("*.jsonl")):
            try:
                with open(log_file, 'r') as f:
                    for line in f:
                        try:
                            event = json.loads(line.strip())
                            event_time = datetime.fromtimestamp(event['timestamp'])
                            if event_time >= cutoff_time:
                                events.append(event)
                        except json.JSONDecodeError:
                            continue
            except Exception as e:
                self.logger.error(f"Error reading log file {log_file}: {e}")
                
        return sorted(events, key=lambda x: x['timestamp'])
        
    def _prune_patterns(self, scale: TimeScale, max_age: timedelta):
        """Remove patterns older than max_age"""
        cutoff_time = datetime.now().timestamp() - max_age.total_seconds()
        self.patterns[scale] = [
            p for p in self.patterns[scale]
            if p.end_time >= cutoff_time
        ]
        
    def _get_all_patterns(self) -> List[CognitivePattern]:
        """Get all patterns across all time scales"""
        all_patterns = []
        for scale in TimeScale:
            all_patterns.extend(self.patterns[scale])
        return sorted(all_patterns, key=lambda p: p.start_time)
        
    def _log_resonance(self, resonance: CognitiveResonance):
        """Log detected resonance"""
        log_entry = {
            'timestamp': datetime.now().timestamp(),
            'type': resonance.type.value,
            'strength': resonance.strength,
            'duration': resonance.duration,
            'emergence_metrics': resonance.emergence_metrics,
            'context': resonance.context
        }
        
        log_file = self.log_dir / 'resonance_log.jsonl'
        try:
            with open(log_file, 'a') as f:
                json.dump(log_entry, f)
                f.write('\n')
        except Exception as e:
            self.logger.error(f"Error logging resonance: {e}")
            
    def _log_development_event(self, event_type: str, details: Dict, files: List[str]):
        """Log a development event"""
        self.development_tracker.track_event(event_type, details, files)
        self.logger.info(f"Development event: {event_type} - {details}")
            
    def _prepare_metrics_for_validation(self) -> pd.DataFrame:
        """Prepare metrics data for validation"""
        metrics = []
        
        # Collect metrics from patterns
        for timescale in self.patterns:
            for pattern in self.patterns[timescale]:
                metrics.append({
                    'timestamp': pattern.start_time,
                    'timescale': timescale.name,
                    **pattern.metrics
                })
                
        # Add development metrics
        dev_metrics = self.development_tracker.get_session_metrics()
        if dev_metrics:
            metrics.extend([{
                'timestamp': datetime.now(),
                'timescale': 'DEVELOPMENT',
                **dev_metrics
            }])
            
        return pd.DataFrame(metrics)
        
    async def load_browser_history(self, history_data: List[Dict]):
        """Load browser history for context analysis"""
        try:
            await self.context_analyzer.load_history(history_data)
            self.logger.info("Browser history loaded successfully")
        except Exception as e:
            self.logger.error(f"Error loading browser history: {e}")
            
if __name__ == '__main__':
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create and start the system
    system = CognitiveFieldSystem()
    asyncio.run(system.start())
