# API Key Management Guide

**How to generate and manage API keys for frontend developers**

---

## 🚀 Quick Start (30 seconds)

### Generate an API Key for Frontend Developer

```bash
cd scripts
python manage_api_keys.py create frontend-prod "Production frontend application"
```

**Output:**
```
🔑 API Key: xK7mP9nQ2rT5vW8yB1cE4fH6jL0oR3sU9wA2dF5gI8k

📋 Give this to your frontend developer:
API_KEY=xK7mP9nQ2rT5vW8yB1cE4fH6jL0oR3sU9wA2dF5gI8k
BASE_URL=http://localhost:5000
```

**That's it!** Send those two lines to your frontend developer.

---

## 📖 Complete Guide

### 1. Create API Key

```bash
# Syntax
python manage_api_keys.py create <name> [description]

# Examples
python manage_api_keys.py create frontend-prod "Production frontend"
python manage_api_keys.py create frontend-dev "Development frontend"
python manage_api_keys.py create mobile-app "Mobile application"
```

### 2. List All Keys

```bash
python manage_api_keys.py list
```

**Output:**
```
API KEYS
======================================================================

1. frontend-prod
   Status: 🟢 Active
   Created: 2025-10-22T10:30:00
   Description: Production frontend
   Key: xK7mP9nQ...dF5gI8k

2. frontend-dev
   Status: 🟢 Active
   Created: 2025-10-22T11:00:00
   Description: Development frontend
   Key: aB2cD3eF...gH4iJ5k
```

### 3. Get Keys for .env File

```bash
python manage_api_keys.py env
```

**Output:**
```
ACTIVE API KEYS FOR .env FILE
======================================================================
Copy this line to your .env file:
----------------------------------------------------------------------
API_KEYS=xK7mP9nQ2rT5vW8yB1cE4fH6jL0oR3sU9wA2dF5gI8k,aB2cD3eF...gH4iJ5k
----------------------------------------------------------------------
```

Copy that line and paste it in your `.env` file!

### 4. Disable a Key (Without Deleting)

```bash
python manage_api_keys.py disable frontend-dev
```

This keeps the key in the system but makes it inactive. Useful for temporary deactivation.

### 5. Enable a Key

```bash
python manage_api_keys.py enable frontend-dev
```

Re-enable a previously disabled key.

### 6. Delete a Key

```bash
python manage_api_keys.py delete frontend-old
```

Permanently remove a key. **Warning:** This cannot be undone!

---

## 📧 What to Send to Frontend Developer

After creating a key, send them this:

```
Hi [Frontend Developer],

Here are your API credentials for the Nigerian Real Estate Scraper:

API Key: xK7mP9nQ2rT5vW8yB1cE4fH6jL0oR3sU9wA2dF5gI8k
Base URL: http://localhost:5000  (or https://api.yourdomain.com)

Add these to your .env file as:

REACT_APP_API_KEY=xK7mP9nQ2rT5vW8yB1cE4fH6jL0oR3sU9wA2dF5gI8k
REACT_APP_API_URL=http://localhost:5000

Complete integration guide: docs/FRONTEND_AUTH_GUIDE.md

Let me know if you need anything!
```

---

## 🔧 Setup Process (One-Time)

### Step 1: Create Keys for Your Environments

```bash
cd scripts

# Production key
python manage_api_keys.py create frontend-prod "Production frontend"

# Development/Testing key
python manage_api_keys.py create frontend-dev "Development and testing"
```

### Step 2: Add Keys to .env File

```bash
# Get all active keys
python manage_api_keys.py env
```

Copy the output and add to your `.env` file:

```bash
# .env file
AUTH_ENABLED=true
API_KEYS=xK7mP9nQ2rT5vW8yB1cE4fH6jL0oR3sU9wA2dF5gI8k,aB2cD3eF...
```

### Step 3: Restart API Server

```bash
python api_server.py
```

Done! Your API now requires authentication.

---

## 🔐 Security Best Practices

### DO ✅

- **Generate separate keys** for different environments (dev, staging, prod)
- **Rotate keys regularly** (every 90 days)
- **Disable unused keys** immediately
- **Keep `api_keys.json` secure** (it's in .gitignore)
- **Use HTTPS in production**
- **Monitor for unauthorized access**

### DON'T ❌

- **Never commit** `api_keys.json` to git
- **Never share keys** in public channels (Slack, email groups)
- **Never use the same key** for multiple environments
- **Never hardcode keys** in frontend code
- **Don't share keys** in screenshots or logs

---

## 🔄 Key Rotation (Every 90 Days)

### Process

1. **Create new key:**
   ```bash
   python manage_api_keys.py create frontend-prod-new "New production key"
   ```

2. **Update .env with both keys (old + new):**
   ```bash
   python manage_api_keys.py env
   # Copy the output to .env
   ```

3. **Restart API server:**
   ```bash
   python api_server.py
   ```

4. **Update frontend with new key**

5. **After frontend deploys, disable old key:**
   ```bash
   python manage_api_keys.py disable frontend-prod-old
   ```

6. **After confirming everything works, delete old key:**
   ```bash
   python manage_api_keys.py delete frontend-prod-old
   ```

---

## 🚨 If a Key is Compromised

**Act immediately:**

```bash
# 1. Disable the compromised key
python manage_api_keys.py disable compromised-key-name

# 2. Update .env file (remove compromised key)
python manage_api_keys.py env

# 3. Restart API server
python api_server.py

# 4. Create new key
python manage_api_keys.py create frontend-prod-new "Replacement key"

# 5. Send new key to frontend team

# 6. Delete compromised key
python manage_api_keys.py delete compromised-key-name
```

---

## 📊 Monitoring

### Check Who's Using Your API

```bash
# View API server logs
tail -f logs/scraper.log | grep "Authentication"
```

You'll see:
```
Authentication successful: frontend-prod
Authentication failed: invalid key
Rate limit exceeded: frontend-dev
```

---

## 🎯 Common Scenarios

### Scenario 1: New Frontend Developer Joins

```bash
# Create a development key for them
python manage_api_keys.py create frontend-alice "Alice's development key"

# Send them the key and documentation
# When they leave, disable/delete the key
```

### Scenario 2: Setting Up Staging Environment

```bash
# Create staging key
python manage_api_keys.py create frontend-staging "Staging environment"

# Add to .env
python manage_api_keys.py env
```

### Scenario 3: Mobile App Launch

```bash
# Create mobile app key
python manage_api_keys.py create mobile-app-prod "Production mobile app"

# Give to mobile team
```

### Scenario 4: Third-Party Integration

```bash
# Create third-party key
python manage_api_keys.py create partner-acme "ACME Corp integration"

# Monitor usage carefully
```

---

## 📁 File Locations

- **API Key Manager:** `scripts/manage_api_keys.py`
- **Keys Database:** `api_keys.json` (auto-created, never commit!)
- **Environment Config:** `.env` (create from `.env.example`)

---

## 💡 Tips

1. **Descriptive Names:** Use names like `frontend-prod`, `mobile-dev` instead of `key1`, `key2`

2. **Documentation:** Add descriptions when creating keys:
   ```bash
   python manage_api_keys.py create key-name "Detailed description here"
   ```

3. **Regular Audits:** Review keys monthly:
   ```bash
   python manage_api_keys.py list
   ```

4. **Separate Keys:** Different key for each:
   - Environment (dev, staging, prod)
   - Application (web, mobile, desktop)
   - Team member (if needed)

5. **Track in Password Manager:** Store keys in 1Password, LastPass, etc.

---

## 🆘 Troubleshooting

### "No such file: api_keys.json"

This is normal! The file is created automatically when you create your first key.

```bash
python manage_api_keys.py create my-first-key "First API key"
```

### "API key required" error when testing

1. Check .env file has `AUTH_ENABLED=true`
2. Check `API_KEYS=...` is set in .env
3. Restart API server
4. Include header in request: `X-API-Key: your-key`

### Keys not working after restart

1. Run: `python manage_api_keys.py env`
2. Copy output to .env file
3. Restart server

---

## 📚 Related Documentation

- **Frontend Integration:** `docs/FRONTEND_AUTH_GUIDE.md`
- **Security Implementation:** `docs/SECURITY_IMPLEMENTATION.md`
- **Testing Guide:** `docs/TESTING_GUIDE.md`

---

## ✅ Quick Reference

| Task | Command |
|------|---------|
| Create key | `python manage_api_keys.py create <name> [desc]` |
| List keys | `python manage_api_keys.py list` |
| Get .env format | `python manage_api_keys.py env` |
| Disable key | `python manage_api_keys.py disable <name>` |
| Enable key | `python manage_api_keys.py enable <name>` |
| Delete key | `python manage_api_keys.py delete <name>` |

---

**Last Updated:** 2025-10-22
**Version:** 1.0
**Status:** ✅ Ready to Use
