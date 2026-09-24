@echo off
chcp 65001 >nul
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

set MISSING=0

echo [1/11] os...
py -c "import os" 2>nul
if %errorlevel% neq 0 (
    echo   -^> ОШИБКА: модуль os не найден (встроенный, странно...)
    set /a MISSING+=1
) else (
    echo   -^> OK
)

echo [2/11] random...
py -c "import random" 2>nul
if %errorlevel% neq 0 (
    echo   -^> ОШИБКА: модуль random не найден (встроенный, странно...)
    set /a MISSING+=1
) else (
    echo   -^> OK
)

echo [3/11] socket...
py -c "import socket" 2>nul
if %errorlevel% neq 0 (
    echo   -^> ОШИБКА: модуль socket не найден (встроенный, странно...)
    set /a MISSING+=1
) else (
    echo   -^> OK
)

echo [4/11] subprocess...
py -c "import subprocess" 2>nul
if %errorlevel% neq 0 (
    echo   -^> ОШИБКА: модуль subprocess не найден (встроенный, странно...)
    set /a MISSING+=1
) else (
    echo   -^> OK
)

echo [5/11] sys...
py -c "import sys" 2>nul
if %errorlevel% neq 0 (
    echo   -^> ОШИБКА: модуль sys не найден (встроенный, странно...)
    set /a MISSING+=1
) else (
    echo   -^> OK
)

echo [6/11] tkinter...
py -c "import tkinter" 2>nul
if %errorlevel% neq 0 (
    echo   -^> не найден. Попробуйте переустановить Python с галочкой "tcl/tk and IDLE".
    set /a MISSING+=1
) else (
    echo   -^> OK
)

echo [7/11] pywin32 (win32com)...
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
    echo   -^> установлен.
) else (
    echo   -^> OK
)

echo [8/11] shutil...
py -c "import shutil" 2>nul
if %errorlevel% neq 0 (
    echo   -^> ОШИБКА: модуль shutil не найден (встроенный, странно...)
    set /a MISSING+=1
) else (
    echo   -^> OK
)

echo [9/11] winreg...
py -c "import winreg" 2>nul
if %errorlevel% neq 0 (
    echo   -^> ОШИБКА: модуль winreg не найден (встроенный на Windows).
    set /a MISSING+=1
) else (
    echo   -^> OK
)

echo [10/11] ctypes...
py -c "import ctypes" 2>nul
if %errorlevel% neq 0 (
    echo   -^> ОШИБКА: модуль ctypes не найден (встроенный, странно...)
    set /a MISSING+=1
) else (
    echo   -^> OK
)

echo [11/11] pathlib...
py -c "import pathlib" 2>nul
if %errorlevel% neq 0 (
    echo   -^> ОШИБКА: модуль pathlib не найден (встроенный, странно...)
    set /a MISSING+=1
) else (
    echo   -^> OK
)

echo.
if %MISSING% neq 0 (
    echo ВНИМАНИЕ: не найдено встроенных модулей: %MISSING%.
    echo Скорее всего проблема с самим Python, а не с зависимостями.
    echo.
)

echo ============================================
echo  Запуск Minesweeper.py с правами администратора...
echo ============================================
py Minesweeper.py
pause