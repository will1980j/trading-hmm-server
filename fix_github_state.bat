@echo off
echo ========================================
echo FIXING GITHUB TO MATCH LOCAL
echo ========================================
echo.
echo Your local repository is at the GOOD commit.
echo GitHub has 3 BAD commits ahead of you.
echo.
echo This will make GitHub match your local state.
echo.
pause

git push origin main --force

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo SUCCESS!
    echo ========================================
    echo.
    echo GitHub now matches your local state.
    echo Railway will redeploy the good version.
) else (
    echo.
    echo ========================================
    echo BLOCKED BY CODE DEFENDER
    echo ========================================
    echo.
    echo Use Railway dashboard to manually redeploy
    echo the good version instead.
)

pause
