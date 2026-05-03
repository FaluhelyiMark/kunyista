@echo off
setlocal EnableDelayedExpansion
title Kunyista Telepito

:: ============================================================
::  KUNYISTA TELEPITO
::  - Python letoltese es telepitese (ha nem talalhato)
::  - kunyista.py letoltese GitHub-rol
::  - Asztali parancsikon letrehozasa
:: ============================================================

:: --- CONFIG ---------------------------------------------------
set "PYTHON_FILE=kunyista.py"
set "APP_NAME=Kunyista"
set "INSTALL_DIR=%LOCALAPPDATA%\Kunyista"
set "RAW_URL=https://raw.githubusercontent.com/FaluhelyiMark/kunyista/main/kunyista.py"
:: ------------------------------------------------------------

echo.
echo  ==========================================
echo    KUNYISTA TELEPITO
echo  ==========================================
echo.

:: ── 1. Python ellenorzese ────────────────────────────────────
echo [1/4] Python ellenorzese...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo  [!] Python nem talalhato. Letoltes folyamatban...

    :: winget-tel probalkozunk eloszor (Win 10/11)
    winget --version >nul 2>&1
    if %errorlevel% == 0 (
        echo  [i] winget talalhato, Python telepitese...
        winget install -e --id Python.Python.3.12 --silent --accept-package-agreements --accept-source-agreements
        if %errorlevel% neq 0 (
            echo  [!] winget telepites nem sikerult, kezi letoltes indul...
            goto :manual_python
        )
    ) else (
        goto :manual_python
    )

    :: PATH frissitese
    set "PATH=%LOCALAPPDATA%\Programs\Python\Python312;%LOCALAPPDATA%\Programs\Python\Python312\Scripts;%PATH%"
    python --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo  [!] Python telepitese utan sem talalhato. Indits ujra egy uj parancssori ablakot!
        pause
        exit /b 1
    )
    echo  [OK] Python sikeresen telepitve.
    goto :check_pip
)

:manual_python
echo  [i] Kezileg tolti le a Python telepitot...
set "PY_INSTALLER=%TEMP%\python_installer.exe"
curl -L -o "%PY_INSTALLER%" "https://www.python.org/ftp/python/3.12.4/python-3.12.4-amd64.exe"
if %errorlevel% neq 0 (
    echo  [HIBA] Nem sikerult letolteni a Python telepitot.
    echo  Kerlek kezi telepitsd: https://www.python.org/downloads/
    pause
    exit /b 1
)
echo  [i] Python telepitese... (ez eltarthat nehany percig)
"%PY_INSTALLER%" /quiet InstallAllUsers=0 PrependPath=1 Include_test=0
del "%PY_INSTALLER%"
set "PATH=%LOCALAPPDATA%\Programs\Python\Python312;%LOCALAPPDATA%\Programs\Python\Python312\Scripts;%PATH%"

:check_pip
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo  [HIBA] Python meg mindig nem talalhato. Telepisd kezi: https://www.python.org/
    pause
    exit /b 1
)
echo  [OK] Python rendben.

:: ── 2. Telepitesi mappa letrehozasa ─────────────────────────
echo.
echo [2/4] Telepitesi mappa elokeszitese...
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"
echo  [OK] Mappa: %INSTALL_DIR%

:: ── 3. Python fajl letoltese GitHub-rol ─────────────────────
echo.
echo [3/4] %PYTHON_FILE% letoltese GitHub-rol...
set "DEST_FILE=%INSTALL_DIR%\%PYTHON_FILE%"

curl -L -o "%DEST_FILE%" "%RAW_URL%"
if %errorlevel% neq 0 (
    echo  [HIBA] Nem sikerult letolteni: %RAW_URL%
    echo  Ellenorizd hogy a repo publikus-e: https://github.com/FaluhelyiMark/kunyista
    pause
    exit /b 1
)
echo  [OK] Letoltve: %DEST_FILE%

:: ── 4. Asztali parancsikon letrehozasa ──────────────────────
echo.
echo [4/4] Asztali parancsikon letrehozasa...

:: Python eleresi ut lekerdezese
for /f "tokens=*" %%i in ('where python') do set "PYTHON_PATH=%%i"

:: .bat launcher letrehozasa az alkalmazas mellé (ikonhoz kell)
set "LAUNCHER=%INSTALL_DIR%\start_kunyista.bat"
(
    echo @echo off
    echo cd /d "%INSTALL_DIR%"
    echo start "" "%PYTHON_PATH%" "%DEST_FILE%"
) > "%LAUNCHER%"

:: PowerShell segitsegevel hozuk letre a .lnk parancsikont
set "SHORTCUT=%USERPROFILE%\Desktop\%APP_NAME%.lnk"
powershell -NoProfile -Command ^
    "$ws = New-Object -ComObject WScript.Shell; ^
     $sc = $ws.CreateShortcut('%SHORTCUT%'); ^
     $sc.TargetPath = '%PYTHON_PATH%'; ^
     $sc.Arguments = '\"'+'%DEST_FILE%'+'\"'; ^
     $sc.WorkingDirectory = '%INSTALL_DIR%'; ^
     $sc.Description = '%APP_NAME% - Windows Optimalizalo'; ^
     $sc.Save()"

if exist "%SHORTCUT%" (
    echo  [OK] Parancsikon letrehozva az asztalon.
) else (
    echo  [!] Parancsikon letrehozasa nem sikerult, de a program futtatható innen:
    echo      %PYTHON_PATH% "%DEST_FILE%"
)

:: ── Kesz ─────────────────────────────────────────────────────
echo.
echo  ==========================================
echo    TELEPITES KESZ!
echo  ==========================================
echo.
echo  Az alkalmazas helye: %INSTALL_DIR%
echo  Inditas: asztalon a "%APP_NAME%" parancsikon
echo.
pause
