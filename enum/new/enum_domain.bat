@echo off
title Mass Subdomain Scanner

echo ==========================================
echo        MASS SUBDOMAIN ENUMERATION
echo ==========================================
echo.

for /f %%d in (d.txt) do (

    echo ------------------------------------------
    echo [TARGET] %%d

    if not exist "%%d" (
        mkdir "%%d"
        echo [DIR]    Created folder %%d
    )

    REM ===== FINDOMAIN =====
    if exist "%%d\findomain.txt" (
        echo [SKIP]   findomain already exists
    ) else (
        echo [RUN]    Running findomain...
        findomain -t %%d -q > "%%d\findomain.txt"
        echo [OK]     Saved %%d\findomain.txt
    )

    REM ===== SUBFINDER =====
    if exist "%%d\subfinder.txt" (
        echo [SKIP]   subfinder already exists
    ) else (
        echo [RUN]    Running subfinder...
        subfinder -d %%d -all -recursive -silent -o "%%d\subfinder.txt"
        echo [OK]     Saved %%d\subfinder.txt
    )

)

echo.
echo ==========================================
echo             SCAN COMPLETE
echo ==========================================
pause
