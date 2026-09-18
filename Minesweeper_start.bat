@echo off
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo Запрос прав администратора...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

cd /d %~dp0

echo ============================================
echo  Проверка и установка зависимостей...
echo ============================================

echo Используется интерпретатор:
py -c "import sys; print(sys.executable)"
echo.

echo [1/1] pywin32...
py -c "import win32com" 2>nul
if %errorlevel% neq 0 (
    echo   -^> не найден, устанавливаю pywin32...
    py -m pip install --upgrade pywin32
    if %errorlevel% neq 0 (
        echo.
        echo ОШИБКА: не удалось установить pywin32.
        pause
        exit /b 1
    )
) else (
    echo   -^> уже установлен.
)

echo.
echo ============================================
echo  Запуск saper.py с правами администратора...
echo ============================================
py Minesweeper.py
pause
