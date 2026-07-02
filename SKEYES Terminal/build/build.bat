@echo off
REM ============================================================
REM  SKEYES Terminal  - Build automatique de l'exe Windows
REM ============================================================
setlocal
cd /d "%~dp0\.."

echo [1/5] Verification de Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERREUR: Python n'est pas installe ou pas dans le PATH.
    pause
    exit /b 1
)

echo [2/5] Installation des dependances (pyinstaller)...
python -m pip install --upgrade pip >nul
python -m pip install -r requirements.txt

echo [3/5] Compilation de l'application en .exe (icone SKEYES incluse)...
python -m PyInstaller ^
    --noconfirm ^
    --onefile ^
    --windowed ^
    --name "SKEYES_Terminal" ^
    --icon "app\icon.ico" ^
    "app\terminal_app.py"

echo [4/5] Copie de la config et de l'icone a cote de l'exe...
copy /y "app\config.json" "dist\config.json" >nul
copy /y "app\icon.ico" "dist\icon.ico" >nul
if not exist "dist\logs" mkdir "dist\logs"

echo [5/5] Nettoyage des fichiers temporaires...
rmdir /s /q build_temp 2>nul
if exist "SKEYES_Terminal.spec" del /q "SKEYES_Terminal.spec"

echo.
echo ============================================================
echo  Termine ! Dans le dossier dist\ tu trouveras :
echo    - SKEYES_Terminal.exe
echo    - config.json   (modifiable sans recompiler)
echo    - icon.ico
echo    - logs\         (sessions sauvegardees via le bouton Save)
echo  IMPORTANT : garde config.json a cote de l'exe pour pouvoir
echo  personnaliser couleurs / police / bannière / variables d'env.
echo ============================================================
pause
