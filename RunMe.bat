@echo off

echo Checking if pip is installed...

pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo pip is not installed. Please install Python and ensure pip is installed.
    exit /b 1
)

echo pip is installed!
echo installing packages.

pip install -r requirements.txt

set current_script="%~f0"
set sh_path="RunMe.sh"

if exist %current_script% (
    del %current_script%
)

if exist %sh_path% (
    del %sh_path%
)