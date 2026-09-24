@echo off
echo ===================================================
echo     Compilation de Djuma et Creation de l'installeur
echo ===================================================

if exist "%~dp0venv\Scripts\python.exe" (
    set "PYTHON=%~dp0venv\Scripts\python.exe"
) else (
    set "PYTHON=python"
)

echo.
echo [1/3] Verification de PyInstaller...
"%PYTHON%" -m pip install pyinstaller

echo.
echo [2/3] Compilation de l'application avec PyInstaller...
"%PYTHON%" -m PyInstaller --name "Djuma" --onefile --windowed --noconsole --noconfirm --clean main.py

if errorlevel 1 (
    echo.
    echo ERREUR : La compilation PyInstaller a echoue.
    pause
    exit /b 1
)

echo.
echo [3/3] Recherche du compilateur Inno Setup (ISCC.exe)...

set "ISCC="
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" set "ISCC=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if exist "C:\Program Files\Inno Setup 6\ISCC.exe" set "ISCC=C:\Program Files\Inno Setup 6\ISCC.exe"
if exist "C:\Program Files (x86)\Inno Setup 5\ISCC.exe" set "ISCC=C:\Program Files (x86)\Inno Setup 5\ISCC.exe"

if defined ISCC (
    echo Compilateur Inno Setup trouve : "%ISCC%"
    echo Creation du programme d'installation Setup_Djuma_v1.0.0.exe...
    "%ISCC%" "%~dp0installer.iss"
    
    if errorlevel 0 (
        echo.
        echo ===================================================
        echo SUCCES ! Le wizard d'installation a ete cree :
        echo "%~dp0installer_output\Setup_Djuma_v1.0.0.exe"
        echo ===================================================
    ) else (
        echo ERREUR lors de la compilation de l'installeur Inno Setup.
    )
) else (
    echo.
    echo [ATTENTION] Inno Setup n'est pas encore installe sur ce systeme.
    echo 1. Telechargez Inno Setup gratuitement sur : https://jrsoftware.org/isdl.php
    echo 2. Installez-le, puis relancez ce script !
    echo.
    echo L'executable portable seul reste disponible dans : "%~dp0dist\Djuma.exe"
)

pause
