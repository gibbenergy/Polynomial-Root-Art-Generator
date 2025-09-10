@echo off
setlocal

set "CONDA_EXE=%~dp0miniconda3\Scripts\conda.exe"
set "ENV_PATH=%~dp0env"

if not exist "%CONDA_EXE%" (
    echo [ERROR] Miniconda not found. Please run install.bat first.
    pause
    exit /b 1
)

if not exist "%ENV_PATH%\" (
    echo Creating conda environment 'env'... This may take a moment.
    "%CONDA_EXE%" create -p "%ENV_PATH%" python=3.11 -y
    if errorlevel 1 ( echo [ERROR] Failed to create conda environment. & pause & exit /b 1 )
)

echo Upgrading pip and installing dependencies...
"%CONDA_EXE%" run -p "%ENV_PATH%" python -m pip install --upgrade pip setuptools wheel > nul
"%CONDA_EXE%" run -p "%ENV_PATH%" pip install -r requirements.txt
if errorlevel 1 ( echo [ERROR] Failed to install dependencies. & pause & exit /b 1 )

echo.
echo Starting Flask application...
start http://localhost:5000
"%CONDA_EXE%" run -p "%ENV_PATH%" python app.py

echo.
echo Server has stopped. Press any key to exit.
pause
endlocal
