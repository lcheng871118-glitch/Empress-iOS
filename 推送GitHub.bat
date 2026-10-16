@echo off
title Push Empress-iOS to GitHub
cd /d "%~dp0"
echo.
echo ============================================
echo   Push Empress-iOS project to GitHub
echo   First push will open a GitHub login window.
echo ============================================
echo.
echo [1/3] Pushing code to main ...
git push -u origin main
if errorlevel 1 goto :fail
echo.
echo [2/3] Creating and pushing tag game-data-v0.4.1 ...
git tag game-data-v0.4.1
git push origin game-data-v0.4.1
if errorlevel 1 goto :fail
echo.
echo [3/3] ALL DONE!
echo.
echo Next on GitHub webpage:
echo   1. Releases - edit draft game-data-v0.4.1
echo   2. Pick tag game-data-v0.4.1 in the Tag dropdown
echo   3. Click Publish release
echo   4. Actions - Build iOS - Run workflow
echo.
pause
exit /b 0
:fail
echo.
echo *** FAILED: check the GitHub login window, then run again ***
pause
exit /b 1