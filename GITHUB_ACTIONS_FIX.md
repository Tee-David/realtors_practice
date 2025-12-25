# GitHub Actions Scrape Failure - Fix Guide

**Date**: 2025-12-25
**Issue**: GitHub Actions workflows failing due to missing FIREBASE_CREDENTIALS secret
**Status**: ❌ REQUIRES USER ACTION

---

## Problem Analysis

The GitHub Actions workflow `.github/workflows/scrape-production.yml` requires a Firebase credentials secret that is currently missing.

**Error Location**: Lines 297, 314-318, 443, 451-456

```yaml
env:
  FIREBASE_CREDENTIALS: ${{ secrets.FIREBASE_CREDENTIALS }}
```

**Failure Point**:
```bash
if [ -z "$FIREBASE_CREDENTIALS" ]; then
  echo "ERROR: FIREBASE_CREDENTIALS secret not set!"
  exit 1
fi
```

---

## Root Cause

The workflow expects a GitHub secret named `FIREBASE_CREDENTIALS` containing the Firebase service account JSON, but this secret has not been added to the repository.

---

## Solution: Add Firebase Credentials Secret

### Step 1: Get Firebase Service Account JSON

The credentials file is located at:
```
backend/realtor-s-practice-firebase-adminsdk-fbsvc-3071684e9a.json
```

You need the **contents** of this JSON file (not the filename).

### Step 2: Add Secret to GitHub Repository

1. **Go to GitHub Repository Settings**
   - Navigate to: https://github.com/Tee-David/realtors_practice/settings/secrets/actions

2. **Click "New repository secret"**

3. **Add the Secret**
   - **Name**: `FIREBASE_CREDENTIALS`
   - **Value**: Paste the **entire contents** of `realtor-s-practice-firebase-adminsdk-fbsvc-3071684e9a.json`

   The JSON should look like:
   ```json
   {
     "type": "service_account",
     "project_id": "realtor-s-practice",
     "private_key_id": "...",
     "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
     "client_email": "firebase-adminsdk-fbsvc@realtor-s-practice.iam.gserviceaccount.com",
     ...
   }
   ```

4. **Click "Add secret"**

### Step 3: Verify Secret is Added

1. Go to: Settings → Secrets and variables → Actions
2. Confirm `FIREBASE_CREDENTIALS` appears in the list
3. You should see: "Secret updated X minutes ago"

---

## Testing the Fix

### Option 1: Manual Workflow Trigger

1. Go to: https://github.com/Tee-David/realtors_practice/actions
2. Click "Production Scraper (Intelligent Auto-Batching)"
3. Click "Run workflow"
4. Set parameters:
   - Max pages: 2 (for quick test)
   - Geocoding: 1
   - Sites: Leave empty (uses all enabled sites)
5. Click "Run workflow"
6. Wait 2-3 minutes
7. Check workflow run status - should be green ✅

### Option 2: API Trigger (from Frontend)

The frontend has a "Trigger Scrape" button that calls:
```
POST /api/scraping/github-actions/trigger
```

This will also trigger the workflow once the secret is added.

---

## Expected Behavior After Fix

### Before (Current - FAILING):
```
ERROR: FIREBASE_CREDENTIALS secret not set!
Go to: Settings → Secrets and variables → Actions
Add secret 'FIREBASE_CREDENTIALS' with Firebase service account JSON
❌ Exit code: 1
```

### After (Fixed - SUCCESS):
```
SUCCESS: Firebase credentials validated
SUCCESS: Firebase credentials configured
Uploading to Firestore (Enterprise Schema v3.1)
✅ Firestore upload completed successfully!
```

---

## Alternative: Use Different Credentials File

If you want to use a different Firebase service account:

1. **Create new service account** in Firebase Console
2. **Download JSON key**
3. **Add to GitHub secret** as shown above
4. **Update workflow** to use new credentials (optional - current workflow is flexible)

---

## Security Notes

### ✅ Good Practices:
- Firebase credentials are stored as GitHub encrypted secrets
- Secrets are never exposed in workflow logs
- Temporary credentials file is deleted after use
- Credentials are validated before use

### ⚠️ Important:
- Never commit Firebase credentials to git
- Never expose credentials in workflow logs
- Use separate service accounts for dev/prod
- Rotate credentials periodically

---

## Verification Checklist

After adding the secret, verify:

- [ ] Secret `FIREBASE_CREDENTIALS` exists in GitHub repository settings
- [ ] Secret contains valid JSON (not just filename)
- [ ] Secret includes `private_key` field with BEGIN/END markers
- [ ] Workflow run completes without "FIREBASE_CREDENTIALS secret not set" error
- [ ] Firestore upload succeeds (check "Upload to Firestore" step)
- [ ] Properties appear in Firebase Console → Firestore Database → properties collection

---

## Troubleshooting

### Error: "Invalid Firebase credentials JSON"

**Cause**: JSON is malformed or incomplete

**Fix**:
1. Copy the ENTIRE contents of the JSON file
2. Ensure BEGIN PRIVATE KEY and END PRIVATE KEY are included
3. Ensure no extra characters or truncation
4. Re-add the secret

### Error: "Permission denied" or "Invalid credentials"

**Cause**: Service account lacks permissions

**Fix**:
1. Go to Firebase Console → Project Settings → Service Accounts
2. Verify service account has "Firebase Admin SDK Admin service account" role
3. Generate new key if needed
4. Update GitHub secret with new key

### Workflow still fails after adding secret

**Cause**: Secret not recognized (GitHub caching issue)

**Fix**:
1. Delete the secret
2. Wait 1 minute
3. Re-add the secret with exact same name: `FIREBASE_CREDENTIALS`
4. Trigger new workflow run

---

## Quick Commands

### View Firebase credentials (local)
```bash
cat backend/realtor-s-practice-firebase-adminsdk-fbsvc-3071684e9a.json
```

### Copy to clipboard (Windows PowerShell)
```powershell
Get-Content backend\realtor-s-practice-firebase-adminsdk-fbsvc-3071684e9a.json | clip
```

### Copy to clipboard (Mac/Linux)
```bash
cat backend/realtor-s-practice-firebase-adminsdk-fbsvc-3071684e9a.json | pbcopy  # Mac
cat backend/realtor-s-practice-firebase-adminsdk-fbsvc-3071684e9a.json | xclip   # Linux
```

---

## Next Steps After Fix

Once the secret is added and workflow succeeds:

1. **Verify Firestore Data**
   ```bash
   python backend/scripts/monitor_firestore.py
   ```

2. **Check Frontend**
   - Visit deployed frontend
   - Properties should load from Firestore
   - Pagination should work

3. **Schedule Regular Scrapes**
   - Consider adding schedule trigger to workflow:
     ```yaml
     on:
       schedule:
         - cron: '0 2 * * *'  # Daily at 2 AM UTC
     ```

---

**Status**: 🔴 BLOCKED - Requires user to add GitHub secret

**Impact**: HIGH - Scraping pipeline broken until secret is added

**Urgency**: HIGH - No new data being collected

**Resolution Time**: 5 minutes (once user has access to GitHub repository settings)

---

*Last Updated: 2025-12-25 09:30 AM*
