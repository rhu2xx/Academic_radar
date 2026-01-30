@echo off
REM Quick start script for Academic Radar (Windows)

echo 🎯 Academic Radar - Quick Start
echo ================================
echo.

REM Check if .env exists
if not exist .env (
    echo 📝 Creating .env file from template...
    copy .env.example .env
    echo ⚠️  Please edit .env and add your API keys!
    echo    Required: OPENAI_API_KEY (or ANTHROPIC_API_KEY^)
    echo    Required: OPENALEX_EMAIL
    echo    Required: SMTP_USER, SMTP_PASS, RECIPIENT_EMAIL
    echo.
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist venv (
    echo 🐍 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔌 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo 📦 Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Create directories
echo 📁 Setting up directories...
if not exist data\user_papers mkdir data\user_papers
if not exist cache mkdir cache
if not exist data\papers mkdir data\papers

REM Run setup check
echo.
echo 🔍 Running configuration check...
python setup.py

echo.
echo ✅ Setup complete!
echo.
echo Next steps:
echo   1. Add your research papers to data\user_papers\
echo   2. Run: python main.py --mode profile
echo   3. Run: python main.py --mode search
echo.

pause
