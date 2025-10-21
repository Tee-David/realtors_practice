# Firebase Secrets Setup Guide

> **Quick Answer**: Use **REPOSITORY SECRETS** (not Environment Secrets)

---

## Repository Secrets vs Environment Secrets

### ✅ Use REPOSITORY SECRETS (Recommended)

**What it is**: Secrets available to ALL workflows in your repository

**When to use**: For credentials that all workflows need (like Firebase)

**How to add**:
1. Go to: `https://github.com/Tee-David/realtors_practice/settings/secrets/actions`
2. Click **"New repository secret"**
3. Name: `FIREBASE_CREDENTIALS`
4. Value: [Paste your Firebase JSON]
5. Click **"Add secret"**

**Advantages**:
- ✅ Simpler setup (one secret for all workflows)
- ✅ Both workflows can access it automatically
- ✅ No additional configuration needed

---

### ❌ Environment Secrets (NOT Recommended for Your Use Case)

**What it is**: Secrets tied to specific environments (e.g., "production", "staging")

**When to use**: When you have MULTIPLE environments with DIFFERENT credentials
- Example: `FIREBASE_CREDENTIALS_STAGING` vs `FIREBASE_CREDENTIALS_PRODUCTION`

**Why NOT use for your case**:
- ❌ More complex setup
- ❌ Requires environment configuration in workflows
- ❌ Overkill for single Firebase project

---

## Step-by-Step: Add Repository Secret

### Step 1: Get Your Firebase Credentials

On your local machine:

```bash
# Windows (PowerShell)
Get-Content realtor-s-practice-firebase-adminsdk-fbsvc-c8563eb2f2.json

# Windows (CMD)
type realtor-s-practice-firebase-adminsdk-fbsvc-c8563eb2f2.json

# Mac/Linux
cat realtor-s-practice-firebase-adminsdk-fbsvc-c8563eb2f2.json
```

**Copy the ENTIRE output** (all the JSON)

### Step 2: Add to GitHub

1. **Go to Repository Settings**:
   ```
   https://github.com/Tee-David/realtors_practice/settings/secrets/actions
   ```

2. **Click "New repository secret"**

3. **Enter details**:
   - **Name**: `FIREBASE_CREDENTIALS` (exactly this - case sensitive!)
   - **Secret**: Paste the entire JSON from Step 1

   It should look like:
   ```json
   {
     "type": "service_account",
     "project_id": "realtor-s-practice",
     "private_key_id": "...",
     "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
     "client_email": "firebase-adminsdk-...@realtor-s-practice.iam.gserviceaccount.com",
     ...
   }
   ```

4. **Click "Add secret"**

### Step 3: Verify

After adding, you should see:
```
FIREBASE_CREDENTIALS
  Updated now by YourUsername
```

**Note**: You CANNOT view the secret after saving (GitHub hides it for security). If you need to change it, you must update/replace it.

---

## Testing Your Secret

### Test with Small Scrape

1. Go to: `https://github.com/Tee-David/realtors_practice/actions`
2. Click **"Nigerian Real Estate Scraper"**
3. Click **"Run workflow"**
4. Settings:
   - Max pages: `2`
   - Geocoding: `0`
   - Sites: `cwlagos` (just one site)
5. Click **"Run workflow"**

**Expected**:
- Workflow completes successfully
- Firestore upload step shows: `[SUCCESS] Loaded Firebase credentials from environment variable`
- No errors about missing credentials

---

## Common Errors & Solutions

### Error: "Firebase credentials not found"

**Cause**: Secret name is wrong or not set

**Solution**:
1. Check secret name is EXACTLY `FIREBASE_CREDENTIALS` (case-sensitive)
2. Verify secret exists in repository settings
3. Try deleting and re-adding the secret

### Error: "Invalid Firebase credentials"

**Cause**: JSON is malformed (copy/paste issue)

**Solution**:
1. Re-copy the ENTIRE JSON (including opening `{` and closing `}`)
2. Don't modify the JSON (no extra spaces, newlines, etc.)
3. Make sure you copied from the actual file, not a text editor that modified it

### Error: "Permission denied"

**Cause**: Your Firebase service account doesn't have Firestore permissions

**Solution**:
1. Go to Firebase Console → Settings → Service Accounts
2. Ensure the service account has "Cloud Datastore User" role
3. Regenerate the key if needed

---

## Security Notes

### ✅ What GitHub Does:
- Encrypts the secret using libsodium
- Masks it in all logs (shows `***`)
- Only allows workflows to access it (not visible in UI)
- Only repository owner can edit/delete

### ✅ What You Should Do:
- ✅ Keep `realtor-s-practice-firebase-adminsdk-fbsvc-c8563eb2f2.json` in `.gitignore`
- ✅ Never commit the credentials file to git
- ✅ Don't share the JSON in messages/emails
- ✅ Regenerate the key if it's ever exposed

### ❌ What NOT to Do:
- ❌ Don't commit credentials to git
- ❌ Don't store credentials in code
- ❌ Don't share credentials in public channels
- ❌ Don't use environment secrets (unless you have multiple environments)

---

## Summary

**Answer**: Use **REPOSITORY SECRETS**

**Path**: `Settings → Secrets and variables → Actions → Repository secrets`

**Name**: `FIREBASE_CREDENTIALS` (exactly this)

**Value**: Entire JSON from your Firebase service account file

**That's it!** Both workflows will automatically use this secret. No additional configuration needed.

---

**Need Help?** Check:
- [GitHub Secrets Documentation](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- `docs/GITHUB_ACTIONS_SETUP.md` in this repository
