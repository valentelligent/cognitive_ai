@echo off
:: Activate Conda environment
call conda activate cog_ai

:: Set CUDA paths
set CUDA_PATH=C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.1
set CUDA_HOME=%CUDA_PATH%
set PATH=%CUDA_PATH%\bin;%PATH%

:: Set Python path
set PYTHONPATH=%CD%;%PYTHONPATH%

:: Configure Git (optional)
git config --local core.autocrlf true
git config --local core.eol lf

:: Print environment info
echo Environment activated! Current settings:
echo Python: %CONDA_PREFIX%\python.exe
echo CUDA: %CUDA_PATH%
echo.
echo Available commands:
echo - run_tests: Run the test suite
echo - dev_setup: Set up development environment
echo - clean: Clean temporary files
echo.

:: Create aliases for common commands
doskey run_tests=pytest tests/
doskey dev_setup=pre-commit install ^& pip install -e .
doskey clean=del /s /q *.pyc ^& del /s /q __pycache__
