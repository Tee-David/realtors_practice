@echo off
REM Quick local test to verify scraping works before GitHub Actions
REM This mimics what GitHub Actions does

echo ========================================
echo TESTING SCRAPE LOCALLY
echo ========================================
echo.

cd backend

echo [1/4] Enabling test site (npc)...
python scripts\enable_sites.py npc
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to enable site!
    exit /b 1
)
echo SUCCESS: Site enabled
echo.

echo [2/4] Running quick scrape (2 pages, no geocode, headless)...
set FIREBASE_SERVICE_ACCOUNT=realtor-s-practice-firebase-adminsdk-fbsvc-3071684e9a.json
set FIRESTORE_ENABLED=1
set RP_PAGE_CAP=2
set RP_GEOCODE=0
set RP_HEADLESS=1
set RP_NO_AUTO_WATCHER=1

python main.py
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Scraper failed!
    exit /b 1
)
echo SUCCESS: Scraper completed
echo.

echo [3/4] Checking export files...
if not exist "exports\sites\npc" (
    echo ERROR: No exports directory created!
    exit /b 1
)

dir /s /b exports\sites\npc\*.csv exports\sites\npc\*.xlsx 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo WARNING: No CSV/XLSX files found in exports!
)
echo.

echo [4/4] Testing Firestore upload...
python scripts\upload_sessions_to_firestore.py
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Firestore upload failed!
    exit /b 1
)

echo.
echo ========================================
echo ALL TESTS PASSED!
echo ========================================
echo.
echo Next steps:
echo 1. Check Firestore Console to verify data uploaded
echo 2. Commit workflow changes to GitHub
echo 3. Trigger GitHub Actions workflow manually
echo 4. Monitor workflow logs for success
echo.

pause
