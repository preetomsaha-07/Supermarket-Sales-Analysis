@echo off
echo =======================================================
echo Starting Supermarket Sales Analysis - Streamlit Frontend
echo =======================================================
cd /d "%~dp0"
call .venv\Scripts\activate
streamlit run frontend\dashboard.py
pause
