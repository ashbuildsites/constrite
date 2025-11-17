@echo off
echo.
echo ========================================
echo  SafeSite AI - Construction Safety Monitor
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate

REM Check if requirements are installed
echo Checking dependencies...
pip show streamlit >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
    echo.
)

REM Check for .env file
if not exist ".env" (
    echo.
    echo WARNING: .env file not found!
    echo Please copy .env.example to .env and add your Gemini API key.
    echo.
    pause
    exit /b 1
)

REM Start Streamlit
echo.
echo Starting SafeSite AI...
echo Access the application at: http://localhost:8501
echo.
echo Press Ctrl+C to stop the server
echo.
streamlit run app.py

pause
