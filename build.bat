@echo off
echo ===================================================
echo     Creation de l'executable Todo List Manager
echo ===================================================

echo.
echo [1/2] Installation de PyInstaller...
pip install pyinstaller

echo.
echo [2/2] Compilation de l'application (cela peut prendre quelques minutes)...
pyinstaller --name "TodoListManager" --windowed --noconsole --noconfirm --clean --icon="icon.ico" main.py

echo.
echo ===================================================
echo Compilation terminee !
echo L'executable se trouve dans le dossier :
echo "%CD%\dist\TodoListManager"
echo ===================================================
pause
