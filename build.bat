@echo off
echo ===================================================
echo     Creation de l'executable Todo List Manager
echo ===================================================

echo.
echo [1/2] Installation de PyInstaller...
pip install pyinstaller

echo.
echo [2/2] Compilation de l'application (cela peut prendre quelques minutes)...
pyinstaller --name "Djuma" --onefile --windowed --noconsole --noconfirm --clean --icon icon.ico main.py

echo.
echo [3/3] Creation de l'installateur avec Inno Setup...
if exist "C:\Users\natha\AppData\Local\Programs\Inno Setup 7 (32-bit)\ISCC.exe" (
    "C:\Users\natha\AppData\Local\Programs\Inno Setup 7 (32-bit)\ISCC.exe" installer.iss
    echo.
    echo ===================================================
    echo Compilation et Creation de l'installateur terminees !
    echo L'installateur se trouve dans le dossier :
    echo "%CD%\dist\Djuma_Setup.exe"
    echo ===================================================
) else (
    echo ===================================================
    echo Compilation terminee !
    echo L'executable se trouve dans le dossier :
    echo "%CD%\dist\Djuma.exe"
    echo.
    echo ATTENTION: Inno Setup n'a pas ete trouve a l'emplacement par defaut.
    echo L'installateur n'a pas pu etre genere automatiquement.
    echo ===================================================
)
pause
