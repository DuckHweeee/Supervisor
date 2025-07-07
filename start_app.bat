@echo off
echo 🏢 Smart Building AI Assistant
echo ================================

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python and try again
    pause
    exit /b 1
)

REM Check if streamlit_app.py exists
if not exist "streamlit_app.py" (
    echo ❌ streamlit_app.py not found in current directory
    echo Please run this script from the directory containing streamlit_app.py
    pause
    exit /b 1
)

REM Check if .env file exists
if not exist ".env" (
    echo ⚠️  .env file not found
    echo Please create a .env file with your GROQ_API_KEY
    echo Example: GROQ_API_KEY=your_api_key_here
    echo.
    echo Continuing anyway...
    timeout /t 3 >nul
)

echo 🚀 Starting Smart Building AI Assistant...
echo 📱 The app will open in your default web browser
echo 🔧 Press Ctrl+C to stop the application
echo ================================

REM Start streamlit app
python -m streamlit run streamlit_app.py --server.headless false --server.port 8501

pause
