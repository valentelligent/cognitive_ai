@echo off
echo Starting Cognitive AI Dashboard Services...

:: Set environment variables
set COGNITIVE_LOG_LEVEL=INFO
set COGNITIVE_DETAILED_LOGGING=true
set COGNITIVE_ENABLE_AUTONOMOUS_MONITORING=true

:: Check Python environment
conda activate cognitive_dashboard || (
    echo Error: Could not activate conda environment
    exit /b 1
)

:: Check PostgreSQL
echo Checking PostgreSQL...
net start postgresql-x64-17 || (
    echo Error: Could not start PostgreSQL
    exit /b 1
)

:: Create logs directory if it doesn't exist
if not exist "logs" mkdir logs

:: Start Backend with logging
cd backend
echo Starting Backend Server...
start cmd /k "conda activate cognitive_dashboard && uvicorn app.main:app --reload --port 3000 --log-level debug > ../logs/backend_%date:~-4,4%%date:~-10,2%%date:~-7,2%.log 2>&1"

:: Start Frontend with logging
cd ../frontend
echo Starting Frontend Server...
start cmd /k "npm run dev > ../logs/frontend_%date:~-4,4%%date:~-10,2%%date:~-7,2%.log 2>&1"

:: Start Health Monitoring
cd ../backend
echo Starting Health Monitor...
start cmd /k "conda activate cognitive_dashboard && python -m app.services.health_monitor > ../logs/health_%date:~-4,4%%date:~-10,2%%date:~-7,2%.log 2>&1"

:: Wait for services to start
timeout /t 5 /nobreak

:: Open dashboard in default browser
start http://localhost:5173

echo Services started! 
echo Dashboard: http://localhost:5173
echo Backend API: http://localhost:3000/docs
echo Logs directory: %cd%\..\logs

:: Monitor services
:monitor
echo Checking service status...
netstat -ano | findstr "3000" > nul
if errorlevel 1 (
    echo Backend service not responding!
    exit /b 1
)
netstat -ano | findstr "5173" > nul
if errorlevel 1 (
    echo Frontend service not responding!
    exit /b 1
)
timeout /t 30 /nobreak
goto monitor
