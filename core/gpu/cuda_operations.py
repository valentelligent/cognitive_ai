"""
CUDA-accelerated operations for cognitive load calculations
"""

import os
import logging
import warnings
from typing import Optional, List, Dict
import numpy as np
try:
    import cupy as cp
    import pynvml
    CUDA_AVAILABLE = True
except ImportError:
    CUDA_AVAILABLE = False
    warnings.warn("CUDA not available. Using CPU fallback.")

class GPUManager:
    def __init__(self, memory_limit: float = 0.8):  # 80% of available memory by default
        """Initialize GPU manager with memory limit as fraction of total memory"""
        self.logger = logging.getLogger(__name__)
        self.memory_limit = memory_limit
        self.cuda_available = False
        self._initialize_gpu()

    def _initialize_gpu(self) -> None:
        """Initialize GPU and CUDA environment with graceful fallback"""
        try:
            if not CUDA_AVAILABLE:
                self.logger.warning("CUDA not available. Using CPU fallback.")
                return

            # Initialize CUDA context
            pynvml.nvmlInit()
            device_count = pynvml.nvmlDeviceGetCount()
            
            if device_count == 0:
                self.logger.warning("No CUDA devices found. Using CPU fallback.")
                return
                
            # Get the first GPU device
            self.handle = pynvml.nvmlDeviceGetHandleByIndex(0)
            self.cuda_available = True
            self.logger.info(f"Successfully initialized GPU: {pynvml.nvmlDeviceGetName(self.handle)}")
            
        except Exception as e:
            self.logger.warning(f"Failed to initialize GPU: {e}. Using CPU fallback.")
            self.cuda_available = False
            
    def get_memory_info(self) -> Dict:
        """Get current GPU memory usage"""
        if not self.cuda_available:
            return {"total": 0, "used": 0, "free": 0}
            
        try:
            info = pynvml.nvmlDeviceGetMemoryInfo(self.handle)
            return {
                "total": info.total,
                "used": info.used,
                "free": info.free
            }
        except Exception as e:
            self.logger.error(f"Error getting GPU memory info: {e}")
            return {"total": 0, "used": 0, "free": 0}

    def accelerate_cognitive_load(self, interaction_data: np.ndarray) -> np.ndarray:
        """
        Accelerate cognitive load calculations using CUDA if available
        Falls back to CPU if CUDA is not available or if memory constraints are exceeded
        """
        try:
            if self.cuda_available:
                return self._gpu_cognitive_load(cp.array(interaction_data))
            return self._cpu_cognitive_load(interaction_data)
        except Exception as e:
            self.logger.error(f"Error in cognitive load calculation: {str(e)}")
            return self._cpu_cognitive_load(interaction_data)

    def _gpu_cognitive_load(self, gpu_data: cp.ndarray) -> np.ndarray:
        """Calculate cognitive load using GPU"""
        try:
            # Example cognitive load calculation
            # You can modify this based on your specific needs
            result = cp.sum(cp.square(gpu_data), axis=1)
            result = cp.exp(-result / (2 * cp.std(gpu_data)))
            return cp.asnumpy(result)
        except Exception as e:
            self.logger.error(f"GPU calculation error: {str(e)}")
            return self._cpu_cognitive_load(cp.asnumpy(gpu_data))

    def _cpu_cognitive_load(self, cpu_data: np.ndarray) -> np.ndarray:
        """Fallback CPU implementation of cognitive load calculation"""
        result = np.sum(np.square(cpu_data), axis=1)
        return np.exp(-result / (2 * np.std(cpu_data)))

    def __del__(self):
        """Cleanup GPU resources"""
        if hasattr(self, 'cuda_available') and self.cuda_available:
            try:
                pynvml.nvmlShutdown()
            except Exception as e:
                self.logger.error(f"Error shutting down NVML: {str(e)}")
