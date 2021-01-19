@echo off
@setlocal enableextensions
@cd /d "%~dp0"

echo Updating UI
pyuic5 ui.ui -o ui.py

echo Running script
python elmocut.py

pause