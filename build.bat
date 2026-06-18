@echo off
setlocal enabledelayedexpansion

echo ============================================================
echo   YoloSide v2.0 - One-Click Build Script
echo ============================================================
echo.

:: Check Python virtual environment
if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] .venv not found. Run: python -m venv .venv
    pause
    exit /b 1
)
set PYTHON=.venv\Scripts\python.exe

:: Check Inno Setup
for %%p in ("D:\Software\Inno Setup 6\ISCC.exe" "C:\Program Files\Inno Setup 6\ISCC.exe" "C:\Program Files (x86)\Inno Setup 6\ISCC.exe") do (
    if exist %%p set ISCC=%%~p
)
if not defined ISCC (
    echo [ERROR] Inno Setup 6 not found. Download: https://jrsoftware.org/isinfo.php
    pause
    exit /b 1
)
echo [OK] Inno Setup: %ISCC%

:: Step 1: Clean previous build
echo.
echo [1/3] Cleaning old build artifacts...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"
echo [OK] Clean done

:: Step 2: PyInstaller build
echo.
echo [2/3] PyInstaller building (estimated 3-8 minutes)...
%PYTHON% -m PyInstaller YoloSide.spec --clean --noconfirm
if %errorlevel% neq 0 (
    echo [ERROR] PyInstaller build failed!
    pause
    exit /b 1
)
echo [OK] PyInstaller build done

:: Verify PyInstaller output exists
if not exist "dist\YoloSide\YoloSide.exe" (
    echo [ERROR] dist\YoloSide\YoloSide.exe not found! PyInstaller may have failed silently.
    pause
    exit /b 1
)

:: Step 3: Inno Setup installer
echo.
echo [3/3] Building installer...
"%ISCC%" installer.iss
if %errorlevel% neq 0 (
    echo [ERROR] Installer build failed! Check Inno Setup compiler output above.
    pause
    exit /b 1
)

:: Verify installer output exists
if not exist "dist\YoloSide_Setup_v2.0.exe" (
    echo [ERROR] dist\YoloSide_Setup_v2.0.exe not found! ISCC may have failed silently.
    pause
    exit /b 1
)

:: Done
echo.
echo ============================================================
echo   Build complete!
echo   Installer: dist\YoloSide_Setup_v2.0.exe
echo   Portable:  dist\YoloSide\YoloSide.exe
echo ============================================================

:: Show file size
for %%f in ("dist\YoloSide_Setup_v2.0.exe") do (
    set /a size_mb=%%~zf / 1048576
    echo   Installer size: !size_mb! MB
)
echo.
pause
