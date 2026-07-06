@echo off
pushd %~dp0

if not "%1"=="am_admin" (
    powershell -Command "Start-Process -Verb RunAs -FilePath '%0' -ArgumentList 'am_admin'"
    exit /b
)

set "exe=%cd%\exe\"
set "src=%cd%\src\"

echo Updating UIs
for %%f in ("%exe%\*.ui") do (
    pyuic6 "%%f" -o "%src%\ui\%%~nf.py"
)

echo Running script
python "%src%elmocut.py"

pause