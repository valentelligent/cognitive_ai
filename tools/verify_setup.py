"""
Verify the complete setup of the cognitive_ai project.
This script checks all dependencies, paths, and components.
"""

import os
import sys
import logging
import platform
import subprocess
from typing import Dict, List, Tuple
import pkg_resources

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

def check_python_version() -> bool:
    """Verify Python version meets requirements."""
    required_version = (3, 10)
    current_version = sys.version_info[:2]
    return current_version >= required_version

def check_cuda_setup() -> Dict[str, bool]:
    """Verify CUDA installation and configuration."""
    cuda_checks = {
        "CUDA_PATH": bool(os.environ.get("CUDA_PATH")),
        "CUDA_HOME": bool(os.environ.get("CUDA_HOME")),
        "nvcc": False,
        "cuda_version": False
    }
    
    try:
        result = subprocess.run(['nvcc', '--version'], 
                              capture_output=True, 
                              text=True)
        cuda_checks["nvcc"] = result.returncode == 0
        if cuda_checks["nvcc"]:
            cuda_checks["cuda_version"] = "12.1" in result.stdout
    except FileNotFoundError:
        pass
    
    return cuda_checks

def check_vs_buildtools() -> bool:
    """Verify Visual Studio build tools installation."""
    if platform.system() != "Windows":
        return False
    
    vs_path = "C:\\Program Files (x86)\\Microsoft Visual Studio\\2019"
    return any(os.path.exists(os.path.join(vs_path, edition)) 
              for edition in ["BuildTools", "Community", "Professional", "Enterprise"])

def check_dependencies() -> List[Tuple[str, bool]]:
    """Check if all required packages are installed with correct versions."""
    required_packages = {
        "numpy": "1.24.0",
        "pandas": "2.0.0",
        "scikit-learn": "1.2.0",
        "keyboard": "0.13.5",
        "mouse": "0.7.1",
        "psutil": "5.9.0",
        "pywin32": "306",
        "sphinx": "7.2.6",
        "cupy-cuda12x": "12.1.0",
        "pynvml": "11.5.0"
    }
    
    results = []
    for package, min_version in required_packages.items():
        try:
            installed_version = pkg_resources.get_distribution(package).version
            meets_requirement = pkg_resources.parse_version(installed_version) >= \
                              pkg_resources.parse_version(min_version)
            results.append((f"{package} (>={min_version})", meets_requirement))
        except pkg_resources.DistributionNotFound:
            results.append((f"{package} (>={min_version})", False))
    
    return results

def check_gpu_available() -> bool:
    """Check if NVIDIA GPU is available and accessible."""
    try:
        import torch
        return torch.cuda.is_available()
    except ImportError:
        return False

def main():
    logger = setup_logging()
    logger.info("Starting setup verification...")
    
    # Check Python version
    python_ok = check_python_version()
    logger.info(f"Python version check: {'OK' if python_ok else 'FAILED'}")
    
    # Check CUDA setup
    cuda_checks = check_cuda_setup()
    logger.info("CUDA setup check:")
    for check, status in cuda_checks.items():
        logger.info(f"  {check}: {'OK' if status else 'FAILED'}")
    
    # Check VS Build Tools
    vs_ok = check_vs_buildtools()
    logger.info(f"Visual Studio Build Tools: {'OK' if vs_ok else 'FAILED'}")
    
    # Check dependencies
    logger.info("Checking dependencies:")
    dep_checks = check_dependencies()
    for dep, status in dep_checks:
        logger.info(f"  {dep}: {'OK' if status else 'FAILED'}")
    
    # Check GPU
    gpu_ok = check_gpu_available()
    logger.info(f"GPU availability: {'OK' if gpu_ok else 'FAILED'}")
    
    # Overall status
    all_ok = (python_ok and 
              all(cuda_checks.values()) and 
              vs_ok and 
              all(status for _, status in dep_checks) and 
              gpu_ok)
    
    logger.info(f"\nOverall setup status: {'OK' if all_ok else 'FAILED'}")
    
    if not all_ok:
        logger.warning("\nAction needed:")
        if not python_ok:
            logger.warning("- Install Python 3.10 or later")
        if not all(cuda_checks.values()):
            logger.warning("- Install CUDA 12.1 and set environment variables")
        if not vs_ok:
            logger.warning("- Install Visual Studio 2019 Build Tools")
        for dep, status in dep_checks:
            if not status:
                logger.warning(f"- Install/upgrade {dep}")
        if not gpu_ok:
            logger.warning("- Check GPU drivers and CUDA installation")

if __name__ == "__main__":
    main()
