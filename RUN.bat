@echo off
pushd %~dp0

set "exe=%cd%\exe\"
set "src=%cd%\src\"

echo Updating UI
pyuic5 "%exe%ui.ui" -o "%src%ui.py"

echo Running script
python "%src%elmocut.py"

pause