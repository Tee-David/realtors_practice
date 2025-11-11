# How to Add Firebase Credentials to GitHub Secrets

## Quick Instructions

### Step 1: Copy the Firebase JSON Content

The complete Firebase service account JSON is in the file:
```
realtor-s-practice-firebase-adminsdk-fbsvc-c8563eb2f2.json
```

You can view it with:
```bash
type realtor-s-practice-firebase-adminsdk-fbsvc-c8563eb2f2.json
```

### Step 2: Add to GitHub Secrets

1. **Go to your GitHub repository**: https://github.com/YOUR_USERNAME/YOUR_REPO_NAME

2. **Navigate to Settings**:
   - Click on **Settings** (top menu)
   - In the left sidebar, click **Secrets and variables** → **Actions**

3. **Create New Secret**:
   - Click the **"New repository secret"** button
   - **Name**: `FIREBASE_CREDENTIALS`
   - **Value**: Copy and paste the ENTIRE content from the JSON file (all 13 lines, from `{` to `}`)

4. **Save**:
   - Click **"Add secret"**

### Step 3: Verify

After adding the secret, your next GitHub Actions workflow run will:
- ✅ Detect Firebase credentials automatically
- ✅ Initialize Firestore successfully
- ✅ Upload scraped properties with enterprise schema
- ✅ Make all 16 Firestore API endpoints functional

---

## What This Fixes

**Before** (Current Error):
```
Firebase credentials not found. Set FIREBASE_SERVICE_ACCOUNT or FIREBASE_CREDENTIALS
Enterprise Firestore upload disabled (initialization failed)
```

**After** (Once Secret is Added):
```
✅ Firebase credentials validated
✅ Firestore initialized from environment variable
✅ Uploading consolidated data to Firestore...
✅ Firestore upload completed successfully!
```

---

## The Complete JSON to Copy

Here's the exact content you need to copy and paste into GitHub Secrets:

```json
{
  "type": "service_account",
  "project_id": "realtor-s-practice",
  "private_key_id": "c8563eb2f2fcef49102b0ef710dd6eda95e3b590",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQDmmWzjGQlHWHNs\nQZWO05Qu+wO/eL+a4CZVvFumh4Ze75TgkgwfwR6dK5jzmdfYx0nkRLRzl03rxPaG\nkHNjltqaJsxlOjQrz7OSWP/34S6xd7c5jIkydATS0c4ipdwX+iE5d0oQPLFeIcqG\naW8nL2uQhE4Q7TGibHSWkHl6gddjUMr3LqVcSrziVaRaKb4pea3+hneZkhFiFfx9\nu1OACDYec8M3Ou12ZuzgCHvuNyDl8ku5e3IIJocjt5AI/7cj2HD101L/hLJtO6Ji\nRZ/Ru4S//xLPH7n0ZKQw5AOxJUgPoYYWI7qZki/vnp3iYWHmOiZXuyBZO/UTmH4W\nNIIu6JPrAgMBAAECggEAE+MfdOZv2mtSaP+u+kZc/UBArn6nZ5/1Lme0L8R4Xi+j\nU0rFKOfqz/s2kauu5c8qHDmgpmdiHPc7m5dRnEEiUTEPZ5uBbFXZUsHCMYqGEGAW\nuSvZmTRQRi457NsJBDhaLS6QgJ37XfbkFHt7TpHUYP5IDUWnhi58T4/eKiaQgMwJ\nBmqO2MjXfxSjof3ImfFE9tcbXGuqKOUAV78l5DebjieGIJmOWPogrQ5GHyMYVeYh\nqBmtQVzW759eqi1b6zfZBQFNhomLDoDGLaC5BlbXhv//4MbTSCSbJ6vOmZs+CowP\nLkmPTAuuuQYKMn73YGDfseCsRsKbdLJgYqSrZc3DgQKBgQD7S9ctGilywsXDwCuu\nQxorry26FPNFLGhc5NeLc1ySs6lP4TphmWhIkcHjohl0Z83rKmqUhA6sllkozesd\nUjfDsuLfrck8ELeXQcHoQoJvY9VCZRIFEgHonPMZvabBeP26GgnvoOVUNyytRXvL\ns1OrPgq7TxfVfBMLQ2hh6p1sGwKBgQDq6mjOKjqkK7HQuF2a35W61N6HXkFgNERO\nCOD9V/il37C2AK7iWZ8We531W3XuCHKqMidFAqO1BzHpbOcH8m5MqBxcf5yXJuVN\nsMeJlWOTMW1xcYpaKZeq5bKrBPwYiMaBDaQjfj9Npb/hXrN/ZoYXsSJv748Y64De\nweZ8MQlUcQKBgFi5f0CSYx38vNyPZhzB3mScFjYEHZxHwJVDywKWeZHmUxo7+GPr\nSRGOPPnFCt25pM+qCzVipteywcoRYjjZBY1YBJhbAJjvghKqie8aRHlVsz8c9k7J\n+9iISaDGADGBKXxioy1zDmU8kc6foMTcDOeCIUHe/BhJFWQ9qYYg0vIPAoGANImi\nUOFu5gKDrRtei+GPOg6bigjRdDOcRxuDPgWrrWU+vyWd9y91/fA9nn8K++ZVxqya\nzbtOY5EtX3gkn0lf07MRTLqZidCAHgT4S1Pmxieaw3FSMOH2cpkWgVsHCnGke35S\nhEGa5MG6DSxB1q9WM/xAqGoaRcd9tdQFuSa6YHECgYAuSITv2JfY0h0Au+oK6lVm\nGgrCXNm7Zu276XuBWxA+9ebtE7yGsklQEgljF611FXIJiYxed5fGBbXmRa2re6pT\nZBerMdMh4JyqvaPKuBfghWxYMz2FFjTwoak3B3UF33G6VNdBMr4NHwPSBlomyBGv\nPLEllAOiBQNeLO5f++5KDA==\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-fbsvc@realtor-s-practice.iam.gserviceaccount.com",
  "client_id": "110096699980500112526",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc%40realtor-s-practice.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}
```

**⚠️ IMPORTANT**: Copy the ENTIRE JSON above (all lines from `{` to `}`) as-is. Don't modify anything!

---

## Testing Locally (Optional)

If you want to test the Firestore connection locally before the workflow runs:

```bash
# Set the environment variable
set FIREBASE_SERVICE_ACCOUNT=realtor-s-practice-firebase-adminsdk-fbsvc-c8563eb2f2.json
set FIRESTORE_ENABLED=1

# Test with a small scrape
python main.py
```

---

## What Your Workflow Does With These Credentials

The workflow (`.github/workflows/scrape-large-batch.yml`) will:

1. **Receive the secret** from GitHub Actions environment
2. **Validate** it's proper JSON format
3. **Create temporary credentials file** during the workflow run
4. **Initialize Firestore** connection
5. **Upload all scraped properties** with enterprise schema:
   - 9 major categories (basic_info, property_details, financial, location, amenities, media, agent_info, metadata, tags)
   - 85+ structured fields
   - Auto-detection of listing_type, furnishing, condition
   - Auto-tagging of premium and hot_deal properties
   - Location intelligence with 50+ Lagos landmarks
6. **Clean up old listings** (archive anything older than 30 days)
7. **Delete temporary credentials** after upload completes
8. **Log results** to workflow summary

---

## Troubleshooting

### If you see "Invalid Firebase credentials JSON"
- Make sure you copied the ENTIRE JSON (from `{` to `}`)
- Check there are no extra spaces or newlines at the beginning/end
- Verify it's valid JSON (should be exactly 13 lines)

### If the workflow still fails
- Check the workflow logs in GitHub Actions
- Look for the specific error message in the "Upload to Firestore" step
- Verify the secret name is exactly `FIREBASE_CREDENTIALS` (case-sensitive)

---

## Security Notes

✅ **Safe**: GitHub Secrets are encrypted and never exposed in logs
✅ **Temporary**: The workflow creates a temp file and deletes it after use
✅ **Isolated**: Each workflow run gets a fresh, isolated environment
✅ **Not committed**: The JSON file is in `.gitignore` (never pushed to GitHub)

---

## Next Steps

1. **Add the secret** following the instructions above
2. **Run your workflow** (e.g., `scrape-large-batch.yml`)
3. **Check the workflow logs** to confirm successful Firestore upload
4. **Verify data in Firebase Console**: https://console.firebase.google.com/project/realtor-s-practice/firestore

Done! Your properties will now be automatically uploaded to Firestore with the enterprise schema.
