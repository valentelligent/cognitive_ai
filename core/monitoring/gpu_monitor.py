"""
GPU Monitoring System for Cognitive AI.

This module provides real-time GPU monitoring capabilities with specific optimizations
for RTX 2080 SUPER and CUDA 12.1.
"""

import logging
from typing import Dict, List, Optional
import time
from dataclasses import dataclass
from datetime import datetime
import threading
import queue

import numpy as np
try:
    import pynvml
    import cupy as cp
    CUDA_AVAILABLE = True
except ImportError:
    CUDA_AVAILABLE = False

@dataclass
class GPUStats:
    """Container for GPU statistics."""
    timestamp: datetime
    memory_used: int
    memory_total: int
    utilization: int
    temperature: int
    power_usage: float
    memory_frequency: int
    graphics_frequency: int

class GPUMonitor:
    """Real-time GPU monitoring system."""
    
    def __init__(self, 
                 memory_threshold: float = 0.8,
                 temp_threshold: int = 80,
                 logging_interval: float = 1.0):
        """
        Initialize GPU monitor.

        Args:
            memory_threshold: Maximum memory usage threshold (0.0-1.0)
            temp_threshold: Maximum temperature threshold in Celsius
            logging_interval: How often to log GPU stats in seconds
        """
        self.logger = logging.getLogger(__name__)
        self.memory_threshold = memory_threshold
        self.temp_threshold = temp_threshold
        self.logging_interval = logging_interval
        self.stats_queue = queue.Queue()
        self._initialize_gpu()
        self._monitoring = False
        self.stats_history: List[GPUStats] = []

    def _initialize_gpu(self) -> None:
        """Initialize NVIDIA Management Library."""
        if not CUDA_AVAILABLE:
            self.logger.warning("CUDA dependencies not available. GPU monitoring disabled.")
            return

        try:
            pynvml.nvmlInit()
            self.handle = pynvml.nvmlDeviceGetHandleByIndex(0)
            self.device_name = pynvml.nvmlDeviceGetName(self.handle).decode('utf-8')
            
            if "RTX 2080" not in self.device_name:
                self.logger.info(f"Running on {self.device_name}. Optimized for RTX 2080 SUPER.")
            
            self.logger.info(f"GPU monitoring initialized for {self.device_name}")
        except pynvml.NVMLError as e:
            self.logger.error(f"Failed to initialize GPU monitoring: {str(e)}")
            CUDA_AVAILABLE = False

    def get_gpu_stats(self) -> Optional[GPUStats]:
        """Get current GPU statistics."""
        if not CUDA_AVAILABLE:
            return None

        try:
            memory = pynvml.nvmlDeviceGetMemoryInfo(self.handle)
            utilization = pynvml.nvmlDeviceGetUtilizationRates(self.handle)
            temperature = pynvml.nvmlDeviceGetTemperature(self.handle, pynvml.NVML_TEMPERATURE_GPU)
            power = pynvml.nvmlDeviceGetPowerUsage(self.handle) / 1000.0  # Convert to Watts
            clocks = pynvml.nvmlDeviceGetClockInfo(self.handle, pynvml.NVML_CLOCK_MEM)
            graphics_clock = pynvml.nvmlDeviceGetClockInfo(self.handle, pynvml.NVML_CLOCK_GRAPHICS)

            return GPUStats(
                timestamp=datetime.now(),
                memory_used=memory.used,
                memory_total=memory.total,
                utilization=utilization.gpu,
                temperature=temperature,
                power_usage=power,
                memory_frequency=clocks,
                graphics_frequency=graphics_clock
            )
        except pynvml.NVMLError as e:
            self.logger.error(f"Error getting GPU stats: {str(e)}")
            return None

    def start_monitoring(self) -> None:
        """Start continuous GPU monitoring in a separate thread."""
        if not CUDA_AVAILABLE:
            return

        def monitor_loop():
            while self._monitoring:
                stats = self.get_gpu_stats()
                if stats:
                    self.stats_queue.put(stats)
                    self.stats_history.append(stats)
                    
                    # Check thresholds
                    memory_usage = stats.memory_used / stats.memory_total
                    if memory_usage > self.memory_threshold:
                        self.logger.warning(
                            f"GPU memory usage ({memory_usage:.1%}) exceeds threshold ({self.memory_threshold:.1%})"
                        )
                    
                    if stats.temperature > self.temp_threshold:
                        self.logger.warning(
                            f"GPU temperature ({stats.temperature}°C) exceeds threshold ({self.temp_threshold}°C)"
                        )
                
                time.sleep(self.logging_interval)

        self._monitoring = True
        self.monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        self.monitor_thread.start()
        self.logger.info("GPU monitoring started")

    def stop_monitoring(self) -> None:
        """Stop GPU monitoring."""
        self._monitoring = False
        if hasattr(self, 'monitor_thread'):
            self.monitor_thread.join()
        self.logger.info("GPU monitoring stopped")

    def get_memory_usage(self) -> Dict[str, float]:
        """Get current memory usage statistics."""
        if not CUDA_AVAILABLE:
            return {"error": "CUDA not available"}

        try:
            memory = pynvml.nvmlDeviceGetMemoryInfo(self.handle)
            return {
                "total_gb": memory.total / 1e9,
                "used_gb": memory.used / 1e9,
                "free_gb": memory.free / 1e9,
                "utilization": memory.used / memory.total
            }
        except pynvml.NVMLError as e:
            self.logger.error(f"Error getting memory usage: {str(e)}")
            return {"error": str(e)}

    def get_performance_metrics(self) -> Dict[str, float]:
        """Get GPU performance metrics."""
        stats = self.get_gpu_stats()
        if not stats:
            return {"error": "Could not get GPU stats"}

        return {
            "utilization": stats.utilization,
            "temperature": stats.temperature,
            "power_watts": stats.power_usage,
            "memory_frequency_mhz": stats.memory_frequency,
            "graphics_frequency_mhz": stats.graphics_frequency
        }

    def __del__(self):
        """Cleanup GPU monitoring resources."""
        self.stop_monitoring()
        if CUDA_AVAILABLE:
            try:
                pynvml.nvmlShutdown()
            except:
                pass
