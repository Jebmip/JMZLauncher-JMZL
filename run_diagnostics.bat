@echo off
echo ========================================
echo JMZLauncher - Ely.by Diagnostic Suite
echo ========================================
echo.
echo This will run diagnostic tests to help identify
echo why Ely.by skins are not showing in-game.
echo.
pause
echo.

echo ========================================
echo 1. COMPREHENSIVE DIAGNOSTIC
echo ========================================
echo.
python diagnose_elyby.py
echo.
echo.

echo ========================================
echo 2. JAVA NETWORK TEST
echo ========================================
echo.
python test_java_network.py
echo.
echo.

echo ========================================
echo 3. VIEW AUTHLIB-INJECTOR LOG
echo ========================================
echo.
python view_authlib_log.py
echo.
echo.

echo ========================================
echo DIAGNOSTIC COMPLETE
echo ========================================
echo.
echo Next steps:
echo 1. Review the output above for any errors
echo 2. Read START_HERE.md for quick fixes
echo 3. Read ELYBY_TROUBLESHOOTING.md for detailed solutions
echo.
echo If Java network test failed:
echo   - Update Java to version 17+
echo   - Check firewall settings
echo   - Temporarily disable antivirus
echo.
echo If Java network test succeeded:
echo   - Delete authlib-injector JAR and restart launcher
echo   - Check authlib-injector.log for details
echo.
pause
