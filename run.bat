@echo off
setlocal

cd /d "%~dp0"

echo Installing required packages...
python.exe -m pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo Unable to install the required packages.
    pause
    exit /b 1
)

echo.
echo Starting Secure Password Manager...
python.exe main.py
if errorlevel 1 (
    echo.
    echo The application stopped with an error.
    pause
    exit /b 1
)

endlocal
