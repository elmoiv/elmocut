@echo off
pushd %~dp0

set "exe=%cd%\exe\"
set "src=%cd%\src\"

echo Updating UIs
pyuic5 "%exe%ui_main.ui" -o "%src%ui_main.py"
pyuic5 "%exe%ui_settings.ui" -o "%src%ui_settings.py"

echo Running script
python "%src%elmocut.py"

pause