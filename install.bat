@echo off
setlocal

echo This script will download and install a self-contained version of Miniconda
echo into a 'miniconda3' folder within this project directory.
echo It will not affect your system PATH or any other Python installations.
echo.
pause

set "CONDA_EXE=%~dp0miniconda3\Scripts\conda.exe"

if exist "%CONDA_EXE%" (
    echo Miniconda is already installed locally.
    echo You can now run start.bat to launch the application.
    goto :end
)

echo Downloading Miniconda installer...
powershell -ExecutionPolicy Bypass -Command "Invoke-WebRequest -Uri https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe -OutFile %~dp0Miniconda3-installer.exe"
if errorlevel 1 (
    echo [ERROR] Failed to download installer. Please check your internet connection.
    goto :end
)

echo Installing Miniconda locally... Please wait.
start /wait "" "%~dp0Miniconda3-installer.exe" /InstallationType=JustMe /RegisterPython=0 /AddToPath=0 /S /D=%~dp0miniconda3
del "%~dp0Miniconda3-installer.exe"

if not exist "%CONDA_EXE%" (
    echo [ERROR] Miniconda installation failed.
    goto :end
)

echo [DEBUG] Setting environment variable to accept Conda TOS...
set "CONDA_PLUGINS_AUTO_ACCEPT_TOS=yes"

echo [DEBUG] Accepting Conda Terms of Service via config...
call "%CONDA_EXE%" config --set plugins.auto_accept_tos yes

echo.
echo Miniconda installation complete.
echo You can now run start.bat to launch the application.

:end
echo.
pause
endlocal
