@echo off
REM Double-click to start the Workflow Hub. It opens in your browser.
cd /d "%~dp0"
python -m hub.app
if errorlevel 1 (
  echo.
  echo The hub could not start. Is Python 3.9+ installed? Try: python --version
  pause
)
