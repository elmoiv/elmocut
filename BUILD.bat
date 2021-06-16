@echo off
pushd %~dp0

set "exe=%cd%\exe\"
set "src=%cd%\src\"

pyuic5 "%exe%ui_main.ui" -o "%src%ui\ui_main.py"
pyuic5 "%exe%ui_about.ui" -o "%src%ui\ui_about.py"
pyuic5 "%exe%ui_settings.ui" -o "%src%ui\ui_settings.py"

python build.py

pause