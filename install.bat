@echo off
setlocal EnableDelayedExpansion
title Kunyista Telepito

:: ============================================================
::  KUNYISTA TELEPITO
:: ============================================================
set "APP_NAME=Kunyista"
set "INSTALL_DIR=%LOCALAPPDATA%\Kunyista"
set "RAW_URL=https://raw.githubusercontent.com/FaluhelyiMark/kunyista/main/kunyista.py"
set "ICO_URL=https://raw.githubusercontent.com/FaluhelyiMark/kunyista/main/kunyista.ico"

echo.
echo  ==========================================
echo    KUNYISTA TELEPITO
echo  ==========================================
echo.

:: 1. Python keresese
echo [1/4] Python ellenorzese...
set "PY="
for /f "tokens=*" %%i in ('where python 2^>nul') do (
    echo %%i | findstr /i "WindowsApps" >nul
    if errorlevel 1 if not defined PY set "PY=%%i"
)
if not defined PY (
    for /d %%d in ("%LOCALAPPDATA%\Programs\Python\Python*") do (
        if exist "%%d\python.exe" set "PY=%%d\python.exe"
    )
)
if not defined PY (
    echo  [!] Python nem talalhato, telepites folyamatban...
    set "PY_INSTALLER=%TEMP%\python_installer.exe"
    curl -L -o "%PY_INSTALLER%" "https://www.python.org/ftp/python/3.12.4/python-3.12.4-amd64.exe"
    "%PY_INSTALLER%" /quiet InstallAllUsers=0 PrependPath=1 Include_test=0
    del "%PY_INSTALLER%"
    set "PY=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
)
echo  [OK] Python: %PY%

:: 2. Mappa + kunyista.py letoltese
echo.
echo [2/4] Fajlok letoltese...
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"
set "PY_FILE=%INSTALL_DIR%\kunyista.py"
set "ICO_FILE=%INSTALL_DIR%\kunyista.ico"
curl -L -o "%PY_FILE%" "%RAW_URL%"
if %errorlevel% neq 0 (
    echo  [HIBA] Nem sikerult letolteni!
    pause
    exit /b 1
)
curl -L -o "%ICO_FILE%" "%ICO_URL%" >nul 2>&1
echo  [OK] Fajlok letoltve.

:: 3. PyInstaller -> Kunyista.exe
echo.
echo [3/4] Kunyista.exe elkeszitese... (ez 1-2 percig tarthat)
"%PY%" -m pip install pyinstaller --quiet 2>nul
set "EXE_FILE=%INSTALL_DIR%\Kunyista.exe"
set "BUILD_DIR=%TEMP%\kunyista_build"
:: Verzioinfo fajl letrehozasa (gyarto, nev az UAC ablakban)
set "VERFILE=%TEMP%\kunyista_ver.txt"
(
    echo VSVersionInfo(
    echo   ffi=FixedFileInfo(
    echo     filevers=^(1,0,0,0^),
    echo     prodvers=^(1,0,0,0^),
    echo     mask=0x3f,
    echo     flags=0x0,
    echo     OS=0x40004,
    echo     fileType=0x1,
    echo     subtype=0x0,
    echo     date=^(0, 0^)
    echo   ^),
    echo   kids=[
    echo     StringFileInfo(
    echo       [
    echo         StringTable(
    echo           u'040904B0',
    echo           [StringStruct^(u'CompanyName', u'Mark Faluhelyi'^),
    echo            StringStruct^(u'FileDescription', u'Kunyista - Windows Optimalizalo'^),
    echo            StringStruct^(u'FileVersion', u'1.0.0'^),
    echo            StringStruct^(u'InternalName', u'Kunyista'^),
    echo            StringStruct^(u'LegalCopyright', u'Mark Faluhelyi'^),
    echo            StringStruct^(u'OriginalFilename', u'Kunyista.exe'^),
    echo            StringStruct^(u'ProductName', u'Kunyista'^),
    echo            StringStruct^(u'ProductVersion', u'1.0.0'^)]
    echo         ^)
    echo       ]
    echo     ^),
    echo     VarFileInfo^([VarStruct^(u'Translation', [1033, 1200]^)]^)
    echo   ]
    echo ^)
) > "%VERFILE%"

"%PY%" -m PyInstaller --noconfirm --onefile --windowed --uac-admin --name "Kunyista" --icon "%ICO_FILE%" --version-file "%VERFILE%" --distpath "%INSTALL_DIR%" --workpath "%BUILD_DIR%" --specpath "%BUILD_DIR%" "%PY_FILE%" >nul 2>&1
del "%VERFILE%"
if exist "%EXE_FILE%" (
    echo  [OK] Kunyista.exe elkeszult.
    if exist "%BUILD_DIR%" rmdir /s /q "%BUILD_DIR%"
) else (
    echo  [!] EXE keszites nem sikerult, Python-nal folytatja...
)

:: 4. Asztali parancsikon
echo.
echo [4/4] Parancsikon letrehozasa...
set "SHORTCUT=%USERPROFILE%\Desktop\%APP_NAME%.lnk"
set "VBS=%TEMP%\kunyista_sc.vbs"
if exist "%EXE_FILE%" (
    (
        echo Set ws = CreateObject^("WScript.Shell"^)
        echo Set sc = ws.CreateShortcut^("%SHORTCUT%"^)
        echo sc.TargetPath = "%EXE_FILE%"
        echo sc.WorkingDirectory = "%INSTALL_DIR%"
        echo sc.IconLocation = "%EXE_FILE%"
        echo sc.Description = "Kunyista - Windows Optimalizalo"
        echo sc.Save
    ) > "%VBS%"
) else (
    set "PYTHONW=%PY:python.exe=pythonw.exe%"
    (
        echo Set ws = CreateObject^("WScript.Shell"^)
        echo Set sc = ws.CreateShortcut^("%SHORTCUT%"^)
        echo sc.TargetPath = "%PYTHONW%"
        echo sc.Arguments = """%PY_FILE%"""
        echo sc.WorkingDirectory = "%INSTALL_DIR%"
        echo sc.IconLocation = "%ICO_FILE%"
        echo sc.Description = "Kunyista - Windows Optimalizalo"
        echo sc.Save
    ) > "%VBS%"
)
cscript //nologo "%VBS%"
del "%VBS%"
if exist "%SHORTCUT%" (
    echo  [OK] Parancsikon letrehozva az asztalon.
) else (
    echo  [!] Parancsikon letrehozasa nem sikerult.
)

echo.
echo  ==========================================
echo    TELEPITES KESZ!
echo  ==========================================
echo.
echo  Inditas: asztalon a "Kunyista" parancsikon
echo.
pause
