# Initialize Cognitive AI project environment

# Add Anaconda to PATH if not already there
$anacondaPath = "C:\ProgramData\Anaconda3"
$anacondaScripts = "C:\ProgramData\Anaconda3\Scripts"
$anacondaLibrary = "C:\ProgramData\Anaconda3\Library\bin"

$env:PATH = "$anacondaPath;$anacondaScripts;$anacondaLibrary;$env:PATH"

# Initialize conda for PowerShell
$initScript = Join-Path $anacondaPath "shell\condabin\conda-hook.ps1"
if (Test-Path $initScript) {
    . $initScript
}

# Create conda environment if it doesn't exist
Write-Host "Checking conda environment..."
$envExists = conda env list | Select-String "cog_ai"
if (-not $envExists) {
    Write-Host "Creating conda environment 'cog_ai'..."
    conda env create -f environment.yml
}

# Activate environment
Write-Host "Activating conda environment..."
conda activate cog_ai

# Install dependencies
Write-Host "Installing project dependencies..."
conda install -y -c conda-forge cupy cuda-toolkit=12.1
conda install -y -c conda-forge pynvml
pip install -r requirements.txt

# Setup development environment
Write-Host "Setting up development environment..."
pip install -e .

Write-Host "Environment setup complete! You can now use the following commands:"
Write-Host "- .\activate_env.ps1 : Activate the environment"
Write-Host "- .\build_docs.ps1   : Build documentation"
Write-Host "- Run-Tests          : Run test suite"
Write-Host "- Setup-Dev          : Setup development tools"
