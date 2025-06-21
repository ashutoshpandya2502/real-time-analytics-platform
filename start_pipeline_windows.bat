@echo off
echo 🎯 Kafka Data Pipeline Startup for Windows
echo ==========================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✅ Python found

REM Check if pip is available
pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ pip is not available
    echo Please ensure pip is installed with Python
    pause
    exit /b 1
)

echo ✅ pip found

REM Install dependencies if requirements.txt exists
if exist requirements.txt (
    echo 📦 Installing Python dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ Failed to install dependencies
        pause
        exit /b 1
    )
    echo ✅ Dependencies installed
) else (
    echo ⚠️  requirements.txt not found
)

REM Check if MongoDB is running
echo 🔍 Checking MongoDB...
netstat -an | findstr ":27017" >nul
if errorlevel 1 (
    echo ❌ MongoDB is not running on port 27017
    echo Please start MongoDB:
    echo   1. Download from https://www.mongodb.com/try/download/community
    echo   2. Install and start the MongoDB service
    echo   3. Or use: net start MongoDB
    pause
    exit /b 1
)
echo ✅ MongoDB is running

REM Check if Kafka is running
echo 🔍 Checking Kafka...
netstat -an | findstr ":9092" >nul
if errorlevel 1 (
    echo ❌ Kafka is not running on port 9092
    echo Please start Kafka using one of these methods:
    echo.
    echo Option 1 - Docker (Recommended):
    echo   docker-compose up -d
    echo.
    echo Option 2 - WSL2:
    echo   wsl --install
    echo   Then follow WSL2 instructions in README.md
    echo.
    echo Option 3 - Manual Kafka installation
    pause
    exit /b 1
)
echo ✅ Kafka is running

echo.
echo 🚀 Starting pipeline components...
echo.

REM Start consumer in background
echo Starting Kafka consumer...
start "Kafka Consumer" cmd /k "python kafka_consumer.py"

REM Wait a moment for consumer to start
timeout /t 3 /nobreak >nul

REM Start dashboard in background
echo Starting Streamlit dashboard...
start "Streamlit Dashboard" cmd /k "streamlit run dashboard.py"

REM Wait a moment for dashboard to start
timeout /t 3 /nobreak >nul

REM Start producer in background
echo Starting data generator...
start "Data Generator" cmd /k "python data_generator.py"

echo.
echo 🎉 Pipeline started successfully!
echo.
echo 📊 Access points:
echo    - Dashboard: http://localhost:8501
echo    - Kafka: localhost:9092
echo    - MongoDB: localhost:27017
echo    - Kafka UI (if using Docker): http://localhost:8081
echo.
echo 📋 Running components:
echo    - Kafka Consumer (PID shown in new window)
echo    - Streamlit Dashboard (PID shown in new window)
echo    - Data Generator (PID shown in new window)
echo.
echo ⏹️  Press any key to close this window...
echo    (Individual components will continue running)
pause 