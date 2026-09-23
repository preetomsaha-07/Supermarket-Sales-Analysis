@echo off
echo ===================================================
echo Starting Supermarket Sales Analysis - Flask Backend
echo ===================================================
cd /d "%~dp0"
call .venv\Scripts\activate
python backend\app.py
pause
