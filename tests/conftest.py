"""
Test configuration and fixtures
"""

import pytest
import os
import sys

# Add the project root directory to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

@pytest.fixture
def mock_events():
    """Fixture providing sample interaction events"""
    from datetime import datetime, timedelta
    
    base_time = datetime.now()
    events = []
    
    # Add keyboard events
    for i in range(10):
        events.append({
            'type': 'keyboard',
            'key': chr(97 + i),  # Letters a-j
            'event_type': 'down',
            'timestamp': base_time + timedelta(seconds=i*0.5)
        })
    
    # Add mouse events
    for i in range(5):
        events.append({
            'type': 'mouse',
            'event_type': 'move',
            'position': (i*10, i*10),
            'timestamp': base_time + timedelta(seconds=5+i*0.5)
        })
    
    # Add window events
    for i in range(3):
        events.append({
            'type': 'window_switch',
            'window_title': f'Window{i}',
            'timestamp': base_time + timedelta(seconds=8+i*2)
        })
    
    return events

@pytest.fixture
def mock_usage_data():
    """Fixture providing sample daily usage data"""
    from datetime import datetime, timedelta
    
    base_date = datetime.now().date()
    return {
        base_date - timedelta(days=i): {
            'duration': 3600 - i*300,  # Decreasing daily usage
            'active_windows': 5 + i,   # Increasing window count
            'task_switches': 10 + i    # Increasing task switches
        }
        for i in range(5)
    }
