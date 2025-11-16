#!/bin/bash

# Move verification and status reports
mv -f API_ENDPOINT_TEST_REPORT.md docs/reports/ 2>/dev/null
mv -f SCRAPER_INTEGRATION_VERIFIED.md docs/reports/ 2>/dev/null
mv -f VERIFICATION_COMPLETE.md docs/reports/ 2>/dev/null
mv -f PRODUCTION_STATUS_REPORT.md docs/reports/ 2>/dev/null
mv -f FINAL_SYSTEM_VERIFICATION.md docs/reports/ 2>/dev/null
mv -f TEST_RESULTS_SUCCESS.md docs/reports/ 2>/dev/null

# Move setup and workflow guides
mv -f GITHUB_ACTIONS_SETUP.md docs/setup-guides/ 2>/dev/null
mv -f WORKFLOW_RUNNING.md docs/reports/ 2>/dev/null
mv -f QUICK_REFERENCE.md docs/setup-guides/ 2>/dev/null

# Move summary and explanation docs
mv -f FINAL_SUMMARY_V3.1.md docs/ 2>/dev/null
mv -f ENTERPRISE_SCHEMA_EXPLAINED.md docs/ 2>/dev/null

# Remove obsolete/duplicate files
rm -f API_TO_WORKFLOW_INTEGRATION.md 2>/dev/null
rm -f COMPLETE_FIX_SUMMARY.md 2>/dev/null
rm -f ENTERPRISE_IMPLEMENTATION_SUMMARY.md 2>/dev/null  
rm -f FIRESTORE_ARCHITECTURE_FIX.md 2>/dev/null
rm -f FRONTEND_TRIGGER_VERIFICATION.md 2>/dev/null
rm -f FULL_SCRAPE_ASSURANCE.md 2>/dev/null
rm -f FULL_SCRAPE_RUNNING.md 2>/dev/null
rm -f GITHUB_TEST_INSTRUCTIONS.md 2>/dev/null
rm -f GITHUB_TEST_STATUS.md 2>/dev/null
rm -f WORKFLOW_ANALYSIS_AND_FIXES.md 2>/dev/null
rm -f WORKFLOW_SIMPLIFICATION_COMPLETE.md 2>/dev/null
rm -f WORKFLOW_STRATEGY.md 2>/dev/null
rm -f WORKFLOWS_FIRESTORE_STATUS.md 2>/dev/null
rm -f workflow_status.json 2>/dev/null

echo "Documentation organized successfully"
