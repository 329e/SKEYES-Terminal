@echo off
REM ============================================================
REM  Cree un raccourci sur le Bureau vers SKEYES_Terminal.exe
REM  (a executer APRES build.bat)
REM ============================================================
setlocal
cd /d "%~dp0\.."

set "EXE_PATH=%cd%\dist\SKEYES_Terminal.exe"
set "ICON_PATH=%cd%\dist\icon.ico"

if not exist "%EXE_PATH%" (
    echo ERREUR: %EXE_PATH% introuvable. Lance d'abord build.bat.
    pause
    exit /b 1
)

powershell -NoProfile -Command ^
    "$s = (New-Object -COM WScript.Shell).CreateShortcut('%USERPROFILE%\Desktop\SKEYES Terminal.lnk');" ^
    "$s.TargetPath = '%EXE_PATH%';" ^
    "$s.IconLocation = '%ICON_PATH%';" ^
    "$s.WorkingDirectory = '%cd%\dist';" ^
    "$s.Save()"

echo Raccourci cree sur le Bureau : "SKEYES Terminal.lnk"
pause
