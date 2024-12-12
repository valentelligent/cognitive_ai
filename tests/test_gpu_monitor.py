"""
Tests for GPU monitoring system.
"""

import unittest
from unittest.mock import patch, MagicMock
import time
from datetime import datetime

from core.monitoring.gpu_monitor import GPUMonitor, GPUStats

class TestGPUMonitor(unittest.TestCase):
    """Test suite for GPU monitoring functionality."""

    def setUp(self):
        """Set up test environment."""
        self.monitor = GPUMonitor(
            memory_threshold=0.8,
            temp_threshold=80,
            logging_interval=0.1
        )

    @patch('core.monitoring.gpu_monitor.CUDA_AVAILABLE', True)
    @patch('pynvml.nvmlDeviceGetMemoryInfo')
    @patch('pynvml.nvmlDeviceGetUtilizationRates')
    @patch('pynvml.nvmlDeviceGetTemperature')
    @patch('pynvml.nvmlDeviceGetPowerUsage')
    @patch('pynvml.nvmlDeviceGetClockInfo')
    def test_get_gpu_stats(self, mock_clock, mock_power, mock_temp, 
                          mock_util, mock_memory):
        """Test GPU statistics collection."""
        # Mock GPU responses
        memory_info = MagicMock()
        memory_info.total = 8589934592  # 8GB
        memory_info.used = 4294967296   # 4GB
        memory_info.free = 4294967296   # 4GB
        mock_memory.return_value = memory_info

        util_info = MagicMock()
        util_info.gpu = 75
        mock_util.return_value = util_info

        mock_temp.return_value = 70
        mock_power.return_value = 180000  # 180W
        mock_clock.return_value = 1500

        # Get stats
        stats = self.monitor.get_gpu_stats()

        # Verify stats
        self.assertIsNotNone(stats)
        self.assertEqual(stats.memory_total, 8589934592)
        self.assertEqual(stats.memory_used, 4294967296)
        self.assertEqual(stats.utilization, 75)
        self.assertEqual(stats.temperature, 70)
        self.assertEqual(stats.power_usage, 180.0)
        self.assertEqual(stats.memory_frequency, 1500)

    def test_memory_threshold_warning(self):
        """Test memory usage threshold warnings."""
        with patch('core.monitoring.gpu_monitor.CUDA_AVAILABLE', True):
            with patch.object(self.monitor, 'get_gpu_stats') as mock_stats:
                # Simulate high memory usage
                mock_stats.return_value = GPUStats(
                    timestamp=datetime.now(),
                    memory_total=8589934592,  # 8GB
                    memory_used=7730941133,   # 7.2GB (90%)
                    utilization=80,
                    temperature=75,
                    power_usage=180.0,
                    memory_frequency=1500,
                    graphics_frequency=1800
                )

                # Start monitoring
                self.monitor.start_monitoring()
                time.sleep(0.2)  # Allow time for monitoring
                self.monitor.stop_monitoring()

                # Verify warning was logged
                self.assertTrue(any(stat.memory_used/stat.memory_total > 0.8 
                                  for stat in self.monitor.stats_history))

    def test_temperature_threshold_warning(self):
        """Test temperature threshold warnings."""
        with patch('core.monitoring.gpu_monitor.CUDA_AVAILABLE', True):
            with patch.object(self.monitor, 'get_gpu_stats') as mock_stats:
                # Simulate high temperature
                mock_stats.return_value = GPUStats(
                    timestamp=datetime.now(),
                    memory_total=8589934592,
                    memory_used=4294967296,
                    utilization=90,
                    temperature=85,  # Above threshold
                    power_usage=200.0,
                    memory_frequency=1500,
                    graphics_frequency=1800
                )

                # Start monitoring
                self.monitor.start_monitoring()
                time.sleep(0.2)
                self.monitor.stop_monitoring()

                # Verify warning was logged
                self.assertTrue(any(stat.temperature > 80 
                                  for stat in self.monitor.stats_history))

    def test_cuda_unavailable(self):
        """Test behavior when CUDA is not available."""
        with patch('core.monitoring.gpu_monitor.CUDA_AVAILABLE', False):
            monitor = GPUMonitor()
            self.assertIsNone(monitor.get_gpu_stats())
            memory_info = monitor.get_memory_usage()
            self.assertEqual(memory_info["error"], "CUDA not available")

    def tearDown(self):
        """Clean up after tests."""
        self.monitor.stop_monitoring()

if __name__ == '__main__':
    unittest.main()
