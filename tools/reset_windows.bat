@echo off
echo [Y.A.T. RESET TOOL]
set "TARGET=%USERPROFILE%\.yat"

echo Target: %TARGET%

if exist "%TARGET%" (
    echo.
    echo WARNUNG: Alles in .yat wird geloescht (Keys, Settings, History).
    set /p choice="Wirklich loeschen? (j/n): "
    if /i "%choice%"=="j" (
        rmdir /s /q "%TARGET%"
        echo [OK] Geloescht.
    ) else (
        echo [INFO] Abgebrochen.
    )
) else (
    echo [INFO] .yat existiert nicht. System ist sauber.
)

pause
