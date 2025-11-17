@echo off
REM Full Production Scrape - All 51 Sites with Firestore Upload
REM This script runs a complete scrape with proper environment variables

echo ================================================================================
echo FULL PRODUCTION SCRAPE (NEW STREAMING UPLOAD ARCHITECTURE)
echo ================================================================================
echo.
echo Configuration:
echo - Sites: All 51 enabled
echo - Max pages per site: 20
echo - Geocoding: Enabled
echo - Firestore: Enabled (STREAMING UPLOADS with retry)
echo - Headless mode: Enabled
echo.
echo Expected duration: 1-2 hours (local)
echo Properties upload to Firestore IN REAL-TIME (one at a time with retry)
echo.
echo ================================================================================
echo.

REM Set environment variables (CRITICAL - Must be set BEFORE running Python)
set FIREBASE_SERVICE_ACCOUNT=realtor-s-practice-firebase-adminsdk-fbsvc-c8563eb2f2.json
set FIRESTORE_ENABLED=1
set RP_GEOCODE=1
set RP_PAGE_CAP=20
set RP_HEADLESS=1
set RP_NO_AUTO_WATCHER=1

echo Starting scraper with streaming Firestore uploads...
echo.

REM Run the scraper
python main.py

echo.
echo ================================================================================
echo SCRAPE COMPLETE!
echo ================================================================================
echo.
echo Verification:
echo 1. Run: python verify_full_scrape.py
echo 2. Or view in Firebase Console: https://console.firebase.google.com/project/realtor-s-practice/firestore
echo.
echo Expected: 1,000+ properties uploaded with enterprise schema (9 categories)
echo.
pause
