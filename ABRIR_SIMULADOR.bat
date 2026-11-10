@echo off
cd /d "%~dp0"
if exist "%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" (
  "%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" simulador.py
  goto fin
)
where py >nul 2>nul
if %errorlevel%==0 (
  py -3 simulador.py
) else (
  python simulador.py
)
:fin
if errorlevel 1 (
  echo Se necesita Python 3.9 o superior y un navegador. Consulte LEEME.txt.
  pause
)
