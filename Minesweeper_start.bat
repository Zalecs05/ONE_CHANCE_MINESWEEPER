@echo off
net session >nul 2>&1
if not "%errorlevel%"=="0" (
    echo Запрос прав администратора...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

cd /d "%~dp0"

echo ============================================
echo  Проверка зависимостей
echo ============================================

py -c "import sys; print('Python:', sys.executable); print(sys.version)"
if errorlevel 1 (
    echo ОШИБКА: не удалось запустить py launcher.
    pause
    exit /b 1
)

echo.
echo [1/3] Стандартные модули...
py -c "import os, random, socket, subprocess, sys, shutil, winreg, ctypes, pathlib; print('OK')"
if errorlevel 1 (
    echo ОШИБКА: не найдены стандартные модули Python.
    echo Похоже, установка Python повреждена.
    pause
    exit /b 1
)

echo.
echo [2/3] tkinter...
py -c "import tkinter; print('OK')"
if errorlevel 1 (
    echo ОШИБКА: tkinter не установлен.
    echo Переустанови Python и отметь галочку tcl/tk and IDLE.
    pause
    exit /b 1
)

echo.
echo [3/3] pywin32...
py -c "import win32com; print('OK')"
if errorlevel 1 (
    echo pywin32 не найден, устанавливаю...
    py -m pip install --upgrade pywin32
    if errorlevel 1 (
        echo ОШИБКА: не удалось установить pywin32.
        pause
        exit /b 1
    )
    py -m pywin32_postinstall -install
    py -c "import win32com; print('OK')"
    if errorlevel 1 (
        echo ОШИБКА: pywin32 установлен, но не импортируется.
        pause
        exit /b 1
    )
)

echo.
echo ============================================
echo  Запуск Minesweeper.py с правами администратора...
echo ============================================
py Minesweeper.py
pause