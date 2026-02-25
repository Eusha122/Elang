@echo off
setlocal enabledelayedexpansion
echo.
echo  ================================================
echo    Elang v0.1.0 Installer
echo    The Elang Programming Language
echo  ================================================
echo.

:: ---- Determine install directory ----
set "INSTALL_DIR=%LOCALAPPDATA%\Elang"
echo  Installing to: %INSTALL_DIR%
echo.

:: ---- Create install directory ----
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

:: ---- Copy elang.exe ----
echo  [..] Installing Elang runtime...
copy /y "%~dp0dist\elang.exe" "%INSTALL_DIR%\elang.exe" >nul 2>&1
if errorlevel 1 (
    echo  [ERROR] Failed to copy elang.exe.
    echo          Make sure 'dist\elang.exe' exists next to this installer.
    pause
    exit /b 1
)
echo  [OK] elang.exe installed.

:: ---- Add to User PATH ----
echo  [..] Adding Elang to your PATH...
for /f "tokens=2*" %%a in ('reg query "HKCU\Environment" /v Path 2^>nul') do set "CURRENT_PATH=%%b"
echo !CURRENT_PATH! | findstr /i /c:"%INSTALL_DIR%" >nul 2>&1
if errorlevel 1 (
    setx PATH "!CURRENT_PATH!;%INSTALL_DIR%" >nul 2>&1
    echo  [OK] Added to PATH.
) else (
    echo  [OK] Already on PATH.
)

:: ---- Install VS Code Extension ----
set "VSCODE_EXT=%USERPROFILE%\.vscode\extensions\elang.elang-language-1.0.0"
echo.
echo  [..] Installing VS Code extension...
if exist "%VSCODE_EXT%" rmdir /s /q "%VSCODE_EXT%"
if exist "%~dp0eusha-language" (
    xcopy /s /e /i /q "%~dp0eusha-language" "%VSCODE_EXT%" >nul 2>&1
    if errorlevel 1 (
        echo  [WARN] Could not install VS Code extension.
    ) else (
        echo  [OK] VS Code extension installed.
    )
) else (
    echo  [SKIP] VS Code extension folder not found.
)

:: ---- Associate .elang files ----
echo.
set /p ASSOC="  Associate .elang files with Elang? (y/n): "
if /i "%ASSOC%"=="y" (
    reg add "HKCU\Software\Classes\.elang" /ve /d "ElangFile" /f >nul 2>&1
    reg add "HKCU\Software\Classes\ElangFile" /ve /d "Elang Source File" /f >nul 2>&1
    reg add "HKCU\Software\Classes\ElangFile\shell\open\command" /ve /d "\"%INSTALL_DIR%\elang.exe\" \"%%1\"" /f >nul 2>&1
    echo  [OK] .elang files associated with Elang.
) else (
    echo  [OK] Skipped.
)

:: ---- Done ----
echo.
echo  ================================================
echo    Installation Complete!
echo  ================================================
echo.
echo  Usage:
echo    elang yourfile.elang
echo.
echo  VS Code:
echo    1. Restart VS Code
echo    2. Open any .elang file
echo    3. Click the Play button or right-click ^> Run Elang File
echo.
echo  NOTE: Restart your terminal for PATH changes to take effect.
echo.
pause
