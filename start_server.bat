@echo off
REM Health Insurance Helper - Quick Start Script
REM This script activates the virtual environment and starts the Django server

echo.
echo ============================================
echo  Health Insurance Helper - Starting Server
echo ============================================
echo.

cd /d "%~dp0health_insurance_helper"

echo Activating virtual environment...
call ..\env\Scripts\activate.bat

echo Running database migrations...
python manage.py migrate

echo.
echo ============================================
echo Starting Django development server...
echo ============================================
echo.
echo Server running at: http://127.0.0.1:8000/
echo Admin panel: http://127.0.0.1:8000/admin/
echo.
echo Press Ctrl+C to stop the server
echo.

python manage.py runserver
