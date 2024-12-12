@echo off
:: Build documentation script for Cognitive AI

:: Activate conda environment
call .\activate_env.bat

:: Clean previous build
echo Cleaning previous documentation build...
rd /s /q docs\_build 2>nul

:: Create API documentation
echo Generating API documentation...
sphinx-apidoc -f -o docs/api_reference core/

:: Build HTML documentation
echo Building HTML documentation...
cd docs
call make html
cd ..

:: Open documentation in browser
echo Opening documentation...
start docs\_build\html\index.html

echo Documentation build complete!
