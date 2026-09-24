@echo off
echo ===================================================
echo     Creation de l'executable Todo List Manager
echo ===================================================

if exist "%~dp0venv\Scripts\python.exe" (
	set "PYTHON=%~dp0venv\Scripts\python.exe"
) else (
	set "PYTHON=python"
)

echo.
echo [1/2] Installation de PyInstaller...
"%PYTHON%" -m pip install pyinstaller

echo.
echo [2/2] Compilation de l'application (cela peut prendre quelques minutes)...
if exist "icon.ico" (
	"%PYTHON%" -m PyInstaller --name "Djuma" --onefile --windowed --noconsole --noconfirm --clean --icon="icon.ico" main.py
) else (
	echo Aucune icone icon.ico trouvee, compilation sans icone personnalisee...
	"%PYTHON%" -m PyInstaller --name "Djuma" --onefile --windowed --noconsole --noconfirm --clean main.py
)

if errorlevel 1 (
	echo.
	echo ERREUR : la compilation a echoue.
	exit /b 1
)

echo.
echo ===================================================
echo Compilation terminee !
echo L'executable se trouve dans le dossier :
echo "%CD%\dist\Djuma.exe"
echo ===================================================
pause
