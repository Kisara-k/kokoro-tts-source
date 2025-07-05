@echo off
SETLOCAL

REM Get the current directory
set SCRIPT_DIR=%~dp0
set SCRIPTS_FOLDER=%SCRIPT_DIR%.scripts\

REM Run .convert.py
echo Running .convert.py...
python "%SCRIPTS_FOLDER%.convert.py"
IF ERRORLEVEL 1 (
    echo .convert.py failed. Exiting.
    EXIT /B %ERRORLEVEL%
)

REM Run .content.py
echo Running .content.py...
python "%SCRIPTS_FOLDER%.content.py"
IF ERRORLEVEL 1 (
    echo .content.py failed. Exiting.
    EXIT /B %ERRORLEVEL%
)

REM Git add, commit, and push
echo Committing changes to Git...
cd /d "%SCRIPT_DIR%"
git add -A
git commit -m "Auto commit after script"
git push

IF ERRORLEVEL 1 (
    echo Git push failed.
    EXIT /B %ERRORLEVEL%
)

echo All tasks completed successfully.
ENDLOCAL
pause
