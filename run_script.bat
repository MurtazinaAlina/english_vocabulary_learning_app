@echo off

cd /d "%~dp0"                                   @REM путь к текущей папке файла
call venv\Scripts\activate.bat                  @REM активация виртуального окружения со всеми зависимостями
venv\Scripts\pythonw.exe main.py                @REM запуск приложения
