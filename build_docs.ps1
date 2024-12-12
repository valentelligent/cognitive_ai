# Build documentation script for Cognitive AI

# Activate conda environment if not already activated
if (-not $env:CONDA_PREFIX) {
    conda activate cog_ai
}

# Install sphinx if not already installed
pip install sphinx sphinx-rtd-theme sphinx-autodoc-typehints

# Clean previous build
Write-Host "Cleaning previous documentation build..."
if (Test-Path "docs\_build") {
    Remove-Item -Path "docs\_build" -Recurse -Force
}

# Create necessary directories
if (-not (Test-Path "docs\api_reference")) {
    New-Item -ItemType Directory -Path "docs\api_reference" -Force
}

# Create API documentation
Write-Host "Generating API documentation..."
sphinx-apidoc -f -o docs/api_reference core/

# Build HTML documentation
Write-Host "Building HTML documentation..."
Push-Location docs
sphinx-build -b html . _build/html
Pop-Location

# Open documentation in browser
Write-Host "Opening documentation..."
if (Test-Path "docs\_build\html\index.html") {
    Start-Process "docs\_build\html\index.html"
} else {
    Write-Host "Documentation build failed. Please check for errors above."
}

Write-Host "Documentation build complete!"
