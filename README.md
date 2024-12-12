# Cognitive AI - Interaction Tracking System

A sophisticated system for tracking and analyzing user interactions with cognitive load metrics.

## Features

### 1. Interaction Tracking
- Keyboard events (keystrokes, typing patterns)
- Mouse events (clicks, positions)
- Active window monitoring
- System resource usage (CPU, Memory, GPU)
- Error-resilient event logging
- Robust data persistence

### 2. Cognitive Load Metrics
- Typing speed (WPM)
- Error rate (backspace frequency)
- Task switching patterns
- Focus duration
- Pause patterns between interactions
- Memory and executive function analysis
- GPU-accelerated cognitive load calculations

### 3. Task Management
- Predefined task types (coding, reading, writing, research)
- Schedule-based tracking
- Manual task control
- Task context awareness
- Error recovery and state preservation
- Adaptive interface management

## System Requirements

### Hardware Requirements
- CPU: Multi-core processor (recommended)
- RAM: Minimum 8GB (16GB+ recommended)
- GPU: NVIDIA RTX 2080 SUPER or better
- Storage: 1GB+ free space
- Display: 1920x1080 resolution (minimum)

### Software Requirements
- Python 3.10+ (via Anaconda)
- CUDA 12.1
- Windows 10/11 (required for pywin32)
- Git (for version control)
- Visual Studio 2019 build tools (for CUDA)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/valentelligent/cognitive_ai.git
cd cognitive_ai
```

2. Create and activate conda environment:
```bash
conda env create -f environment.yml
conda activate cog_ai
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

## Dependencies

### Core Dependencies
- numpy>=1.24.0: Scientific computing and data processing
- pandas>=1.3.0: Data manipulation and analysis
- scikit-learn>=0.24.2: Machine learning utilities
- cupy-cuda12x>=13.0.0: GPU acceleration

### System Monitoring
- keyboard>=0.13.5: Keyboard event monitoring
- mouse>=0.7.1: Mouse event monitoring
- psutil>=5.9.0: System resource monitoring
- pywin32>=306: Windows API access
- nvidia-ml-py>=12.0.0: GPU monitoring

### Development Tools
- pytest>=7.0.0: Testing framework
- black>=22.0.0: Code formatting
- isort>=5.10.0: Import sorting
- mypy>=0.950: Static type checking
- flake8>=4.0.0: Code linting
- sphinx>=7.0.0: Documentation generation

## Usage

### Basic Usage
```python
from core.monitoring.cognitive_tracker import CognitiveInteractionTracker

# Initialize tracker with error handling
tracker = CognitiveInteractionTracker(log_dir="interaction_logs")

# Start tracking
tracker.start()

# Start a specific task
tracker.start_task("coding")

# Stop tracking
tracker.stop()
```

### Error Handling
The system includes robust error handling:
```python
try:
    tracker.start_task("coding")
    # Your code here
except Exception as e:
    # Events are preserved in memory even if file operations fail
    print(f"Error: {e}")
finally:
    tracker.stop()  # Cleanup is guaranteed
```

## Data Collection

Data is stored in JSONL format in the `interaction_logs` directory. Each event includes:
- Timestamp
- Event type (keyboard, mouse, task_start, task_end)
- Context (keys pressed, mouse positions)
- Window information
- System metrics
- Cognitive load metrics
- Error context (if applicable)

Example event:
```json
{
    "timestamp": 1733999810.384,
    "event_type": "keyboard",
    "context": {
        "key": "a",
        "scan_code": 30,
        "cognitive_load": {
            "typing_speed": 65.2,
            "error_rate": 0.02,
            "focus_score": 0.85
        }
    },
    "window_title": "cognitive_ai - VS Code",
    "application": "Code.exe",
    "cpu_usage": 15.4,
    "memory_usage": 60.5,
    "gpu_usage": 30.1
}
```

## Testing

### Running Tests
```bash
# Run all tests with verbosity
python -m unittest discover -s tests -v

# Run specific test file
python -m unittest tests/test_interaction_tracker.py
```

### Test Coverage
The test suite includes:
- Cognitive Metrics Tests
  - Behavioral change detection
  - Cognitive load calculation
  - Executive function metrics
  - Language metrics
  - Memory metrics
  - Perception and action metrics
  - Usage pattern metrics
- Cognitive Interaction Tracker Tests
  - Initialization
  - Interaction tracking
  - Task management
  - Schedule validation
  - Error recovery
- Interaction Tracker Tests
  - Event handling (keyboard, mouse)
  - Window tracking
  - System metrics
  - Logging functionality
  - Resource cleanup

## Error Handling and Recovery

The system implements robust error handling:
1. **File Operations**
   - Graceful handling of I/O errors
   - In-memory event preservation
   - Automatic recovery attempts

2. **System Resources**
   - Monitoring of system resource availability
   - Cleanup of resources on shutdown
   - Prevention of resource leaks

3. **Data Integrity**
   - Event buffering
   - Safe event flushing
   - Error context preservation

## Contributing

1. Fork the repository
2. Create a feature branch
3. Implement changes with tests
4. Ensure all tests pass
5. Submit a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and feature requests, please use the GitHub issue tracker.
