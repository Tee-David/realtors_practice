# How to Get API Key (Super Simple!)

> **⚠️ IMPORTANT: DO NOT DELETE THIS FILE!**
> This is the main guide for generating API keys for frontend developers.
> Keep this file - it's essential for onboarding and API access management.

**3 steps to give your frontend developer an API key**

---

## ℹ️ About API Keys

- **Do API keys expire?** No! API keys are permanent until you manually disable them
- **How long do they last?** Forever (until you delete them)
- **Can I have multiple keys?** Yes! Generate different keys for dev/staging/prod
- **Are they secure?** Yes, as long as you don't commit them to git (they're in .gitignore)

---

## Method 1: Super Quick (1 Command)

```bash
python -c "import secrets; print('API_KEY=' + secrets.token_urlsafe(32))"
```

**That's it!** Copy the output and give it to your frontend developer.

**Example Output:**
```
API_KEY=xK7mP9nQ2rT5vW8yB1cE4fH6jL0oR3sU9wA2dF5gI8k
```

---

## Method 2: Using the Script (Recommended)

### Step 1: Generate Key
```bash
cd scripts
python manage_api_keys.py create frontend
```

### Step 2: Copy the Key
You'll see this:
```
🔑 API Key: xK7mP9nQ2rT5vW8yB1cE4fH6jL0oR3sU9wA2dF5gI8k
```

### Step 3: Give to Frontend Developer
Send them exactly this message:

```
Hi!

Your API key: xK7mP9nQ2rT5vW8yB1cE4fH6jL0oR3sU9wA2dF5gI8k
API URL: http://localhost:5000

Add to your .env file:
REACT_APP_API_KEY=xK7mP9nQ2rT5vW8yB1cE4fH6jL0oR3sU9wA2dF5gI8k
REACT_APP_API_URL=http://localhost:5000

Done! Check docs/FRONTEND_AUTH_GUIDE.md for examples.
```

**Done!** That's all you need to do.

---

## What the Frontend Developer Does

They just add it to their `.env` file:

```
REACT_APP_API_KEY=xK7mP9nQ2rT5vW8yB1cE4fH6jL0oR3sU9wA2dF5gI8k
REACT_APP_API_URL=http://localhost:5000
```

Then use it in their code:
```javascript
fetch('http://localhost:5000/api/data/master', {
  headers: {
    'X-API-Key': process.env.REACT_APP_API_KEY
  }
})
```

---

## Common Commands (If You Want)

```bash
# Create a key
python scripts/manage_api_keys.py create my-key

# See all your keys
python scripts/manage_api_keys.py list

# Get keys for your .env file
python scripts/manage_api_keys.py env
```

---

## That's Literally It!

**To give frontend developer an API key:**

1. Run: `python -c "import secrets; print('API_KEY=' + secrets.token_urlsafe(32))"`
2. Copy the output
3. Send to frontend developer

**3 seconds. Done.**

---

## FAQ

### Do I need to regenerate keys regularly?

**No!** API keys don't expire. However, it's good practice to rotate them every 90 days for security.

### What if I want to disable a key?

Use the management script:
```bash
python scripts/manage_api_keys.py disable key-name
```

### What's the difference between API Keys and JWT?

- **API Keys:** Never expire, simpler, good for apps/services
- **JWT Tokens:** Expire after 24 hours, better for user accounts

For most frontend apps, **use API Keys** (simpler!).

### Can I see all my keys?

```bash
python scripts/manage_api_keys.py list
```

### Where are keys stored?

In `api_keys.json` (auto-created, never committed to git).

---

**Note:** The `manage_api_keys.py` script is just a fancy way to organize multiple keys. You don't need it if you just want one quick key.

---

> **⚠️ REMINDER: DO NOT DELETE THIS FILE - IT'S ESSENTIAL!**
