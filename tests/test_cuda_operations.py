"""
Tests for CUDA-accelerated operations
"""

import unittest
import numpy as np
from unittest.mock import patch, MagicMock
import sys
import os

# Add parent directory to path to import core modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.gpu.cuda_operations import GPUManager

class TestGPUManager(unittest.TestCase):
    def setUp(self):
        self.gpu_manager = GPUManager(memory_limit=0.8)
        self.test_data = np.random.rand(1000, 100)  # Test data matrix

    def test_initialization(self):
        """Test GPU manager initialization"""
        self.assertIsNotNone(self.gpu_manager)
        self.assertEqual(self.gpu_manager.memory_limit, 0.8)

    @patch('core.gpu.cuda_operations.CUDA_AVAILABLE', True)
    @patch('pynvml.nvmlDeviceGetMemoryInfo')
    def test_memory_info(self, mock_memory_info):
        """Test GPU memory information retrieval"""
        mock_memory = MagicMock()
        mock_memory.total = 8589934592  # 8GB
        mock_memory.used = 1073741824   # 1GB
        mock_memory.free = 7516192768   # 7GB
        mock_memory_info.return_value = mock_memory

        memory_info = self.gpu_manager.get_memory_info()
        self.assertEqual(memory_info['total'], 8589934592)
        self.assertEqual(memory_info['used'], 1073741824)
        self.assertEqual(memory_info['free'], 7516192768)

    def test_cognitive_load_calculation(self):
        """Test cognitive load calculation with CPU fallback"""
        result = self.gpu_manager.accelerate_cognitive_load(self.test_data)
        self.assertEqual(result.shape[0], self.test_data.shape[0])
        self.assertTrue(np.all(result >= 0) and np.all(result <= 1))

    @patch('core.gpu.cuda_operations.CUDA_AVAILABLE', False)
    def test_cpu_fallback(self):
        """Test CPU fallback when CUDA is not available"""
        gpu_manager = GPUManager()
        result = gpu_manager.accelerate_cognitive_load(self.test_data)
        self.assertEqual(result.shape[0], self.test_data.shape[0])

    def test_memory_constraint_handling(self):
        """Test handling of memory constraints"""
        # Create large data that would exceed typical GPU memory
        large_data = np.random.rand(10000, 10000)
        result = self.gpu_manager.accelerate_cognitive_load(large_data)
        self.assertEqual(result.shape[0], large_data.shape[0])

if __name__ == '__main__':
    unittest.main()
