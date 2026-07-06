@echo off
pushd %~dp0

set "exe=%cd%\exe\"
set "src=%cd%\src\"

echo Updating UIs
for %%f in ("%exe%\*.ui") do (
    pyuic6 "%%f" -o "%src%\ui\%%~nf.py"
)

python build.py

pause