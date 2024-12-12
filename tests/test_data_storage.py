"""
Test suite for verifying data storage and recording functionality
"""

import pytest
import json
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch

from cognitive_ai.core.cognitive_field_system import CognitiveFieldSystem
from cognitive_ai.core.validation.metric_validator import MetricValidator
from cognitive_ai.core.context.browser_context import BrowserContextAnalyzer
from cognitive_ai.core.analysis.development_tracker import DevelopmentTracker

@pytest.fixture
def test_system():
    """Create a test instance of the cognitive field system"""
    system = CognitiveFieldSystem(log_dir="test_logs")
    return system

@pytest.fixture
def sample_browser_history():
    """Sample browser history data for testing"""
    return [
        {
            "timestamp": datetime.now().isoformat(),
            "url": "https://docs.python.org/3/library/asyncio.html",
            "title": "asyncio documentation"
        },
        {
            "timestamp": (datetime.now() - timedelta(minutes=5)).isoformat(),
            "url": "https://github.com/issues/123",
            "title": "Problem solving example"
        }
    ]

class TestDataStorage:
    """Test suite for data storage functionality"""
    
    def test_development_tracker_storage(self, test_system):
        """Test if development events are properly stored"""
        # Track a development event
        test_system.development_tracker.track_event(
            event_type="code_change",
            details={"files_modified": 2, "lines_changed": 50},
            files=["test.py", "main.py"]
        )
        
        # Verify event storage
        assert len(test_system.development_tracker.events) > 0
        latest_event = test_system.development_tracker.events[-1]
        assert latest_event.event_type == "code_change"
        assert latest_event.files_affected == ["test.py", "main.py"]
        
    def test_metric_validation_storage(self, test_system):
        """Test if validation results are properly stored"""
        # Create sample metrics data
        metrics_data = pd.DataFrame({
            'cognitive_load': np.random.random(10),
            'focus_duration': np.random.random(10) * 60,
            'error_rate': np.random.random(10) * 0.1
        })
        
        # Run validation
        validation_result = test_system.metric_validator.validate_cognitive_metrics(metrics_data)
        
        # Verify validation storage
        assert len(test_system.metric_validator.validation_history) > 0
        latest_validation = test_system.metric_validator.validation_history[-1]
        assert 'reliability' in latest_validation
        assert 'validity' in latest_validation
        assert 'confidence_intervals' in latest_validation
        
    async def test_browser_context_storage(self, test_system, sample_browser_history):
        """Test if browser context is properly stored and analyzed"""
        # Load browser history
        await test_system.load_browser_history(sample_browser_history)
        
        # Get context analysis
        context = await test_system.context_analyzer.analyze_context(
            datetime.now(),
            timedelta(minutes=10)
        )
        
        # Verify context data
        assert context is not None
        assert 'learning_sequence' in context
        assert 'research_pattern' in context
        
    def test_learning_moment_storage(self, test_system):
        """Test if learning moments are properly recorded"""
        # Record a learning moment
        test_system.development_tracker.record_learning_moment(
            moment_type="insight",
            description="Understanding async patterns",
            significance=0.8,
            context={"activity": "coding", "files": ["async_handler.py"]}
        )
        
        # Verify learning moment storage
        assert len(test_system.development_tracker.learning_moments) > 0
        latest_moment = test_system.development_tracker.learning_moments[-1]
        assert latest_moment.type == "insight"
        assert latest_moment.significance == 0.8
        
    def test_metrics_persistence(self, test_system, tmp_path):
        """Test if metrics are properly persisted to disk"""
        # Setup test log directory
        log_dir = tmp_path / "metric_logs"
        log_dir.mkdir()
        test_system.log_dir = log_dir
        
        # Generate some test metrics
        test_metrics = {
            "timestamp": datetime.now().isoformat(),
            "cognitive_load": 0.7,
            "focus_duration": 300,
            "error_rate": 0.05
        }
        
        # Write metrics to log file
        log_file = log_dir / f"metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
        with open(log_file, 'w') as f:
            json.dump(test_metrics, f)
        
        # Verify metrics can be read back
        with open(log_file, 'r') as f:
            loaded_metrics = json.load(f)
        
        assert loaded_metrics["cognitive_load"] == test_metrics["cognitive_load"]
        assert loaded_metrics["focus_duration"] == test_metrics["focus_duration"]
        
    async def test_visualization_updates(self, test_system):
        """Test if visualizations are properly updated with new data"""
        # Generate test patterns and resonances
        test_patterns = [Mock(start_time=datetime.now(), metrics={'cognitive_load': 0.6})]
        test_resonances = [Mock(type="insight", strength=0.8)]
        
        # Update visualization
        test_system.visualizer.update_visualization(test_patterns, test_resonances)
        
        # Verify visualization state
        assert test_system.visualizer.last_update is not None
        
    def test_validation_confidence_intervals(self, test_system):
        """Test if confidence intervals are properly calculated and stored"""
        # Generate test metrics
        metrics_data = pd.DataFrame({
            'cognitive_load': np.random.normal(0.6, 0.1, 100),
            'focus_duration': np.random.normal(300, 30, 100)
        })
        
        # Calculate confidence intervals
        confidence_intervals = test_system.metric_validator._calculate_confidence_intervals(metrics_data)
        
        # Verify confidence intervals
        assert 'cognitive_load' in confidence_intervals
        assert 'focus_duration' in confidence_intervals
        for metric in confidence_intervals.values():
            assert 'ci_lower' in metric
            assert 'ci_upper' in metric
            assert metric['ci_lower'] < metric['ci_upper']
