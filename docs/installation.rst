Installation Guide
=================

This guide provides step-by-step instructions for setting up the Cognitive AI system.

Prerequisites
------------

1. **Hardware Requirements**:

   * NVIDIA RTX 2080 SUPER or compatible GPU
   * 8GB+ GPU Memory
   * 16GB+ System RAM
   * Windows 10/11 (64-bit)

2. **Software Requirements**:

   * `Visual Studio 2019 Build Tools <https://visualstudio.microsoft.com/vs/older-downloads/>`_ with:
     
     - C++ build tools
     - Windows 10 SDK
     - MSVC v142 build tools
   
   * `CUDA Toolkit 12.1 <https://developer.nvidia.com/cuda-toolkit>`_
   * `Anaconda <https://www.anaconda.com/products/distribution>`_ (Python 3.10)
   * Git (for version control)

Installation Steps
----------------

1. Install Visual Studio 2019 Build Tools
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

   1. Download Visual Studio 2019 Build Tools
   2. Run the installer
   3. Select "C++ build tools" workload
   4. Install selected components

2. Install CUDA Toolkit
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

   1. Download CUDA Toolkit 12.1
   2. Run installer with default options
   3. Verify installation:
      - Open Command Prompt
      - Run: nvcc --version

3. Configure Environment Variables
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: powershell

   # Run in PowerShell as Administrator
   [Environment]::SetEnvironmentVariable("CUDA_PATH", "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.1", "Machine")
   [Environment]::SetEnvironmentVariable("CUDA_HOME", "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.1", "Machine")
   
   # Add to system PATH
   $cudaPath = "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.1\bin"
   $currentPath = [Environment]::GetEnvironmentVariable("Path", "Machine")
   if ($currentPath -notlike "*$cudaPath*") {
       [Environment]::SetEnvironmentVariable("Path", "$currentPath;$cudaPath", "Machine")
   }

4. Clone Repository
~~~~~~~~~~~~~~~~

.. code-block:: bash

   git clone https://github.com/valentelligent/cognitive_ai.git
   cd cognitive_ai

5. Create and Activate Conda Environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Create environment
   conda env create -f environment.yml
   
   # Activate environment
   conda activate cog_ai

6. Install Additional Dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Install required packages
   pip install pywin32>=306 nvidia-ml-py>=11.5.0

7. Verify Installation
~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Run verification script
   python tools/verify_setup.py

   # Run tests
   python run_tests.py

Development Setup
---------------

For development work, additional tools are configured automatically:

* Pre-commit hooks (code quality)
* Black (code formatting)
* isort (import sorting)
* mypy (type checking)
* flake8 (linting)

Set up development tools:

.. code-block:: bash

   # Install pre-commit hooks
   pre-commit install
   
   # Install development dependencies
   pip install -e ".[dev]"

Documentation
------------

Build and view documentation:

.. code-block:: bash

   # Install documentation dependencies
   pip install -e ".[docs]"
   
   # Build documentation
   cd docs
   make html
   
   # Auto-rebuild on changes
   make livehtml

Troubleshooting
--------------

Common Issues
~~~~~~~~~~~~

1. **CUDA Not Found**
   
   * Check CUDA installation: ``nvcc --version``
   * Verify environment variables:
     
     .. code-block:: bash
     
        echo %CUDA_PATH%
        echo %CUDA_HOME%
        
   * Restart computer after setting environment variables

2. **GPU Not Detected**
   
   * Update NVIDIA drivers
   * Check Device Manager
   * Verify GPU status: ``nvidia-smi``
   * Look for CUDA errors in logs

3. **Build Errors**
   
   * Verify VS2019 Build Tools installation
   * Check Windows SDK version
   * Ensure MSVC v142 is installed

4. **Memory Issues**
   
   * Monitor GPU memory: ``nvidia-smi -l 1``
   * Check system RAM usage
   * Adjust memory limits in config

Getting Help
~~~~~~~~~~~

If you encounter issues:

1. Check the logs in ``interaction_logs/``
2. Run verification script: ``python tools/verify_setup.py``
3. Review :ref:`FAQ <faq>`
4. File an issue on GitHub

Version Compatibility
------------------

Tested configurations:

* Windows 10/11 (64-bit)
* Python 3.10 (Anaconda)
* CUDA 12.1
* VS2019 Build Tools
* RTX 2080 SUPER
