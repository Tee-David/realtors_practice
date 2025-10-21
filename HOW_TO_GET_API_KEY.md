# How to Get API Key (Super Simple!)

**3 steps to give your frontend developer an API key**

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

**Note:** The `manage_api_keys.py` script is just a fancy way to organize multiple keys. You don't need it if you just want one quick key.
