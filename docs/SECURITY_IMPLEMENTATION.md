# Security Implementation Guide

**How to enable security features that have been prepared**

The security features have been **implemented and are ready to use**. They are currently **disabled by default** for development convenience.

---

## 🎯 What's Already Implemented

✅ **Authentication System** (`core/auth.py`)
- API Key authentication
- JWT token authentication
- Flexible decorators for both methods

✅ **Security Middleware** (`core/security.py`)
- Security headers (CSP, XSS Protection, etc.)
- CORS configuration
- Input validation
- Path traversal protection
- Error handlers

✅ **Environment Configuration** (`.env.example`)
- All security settings documented
- Example values provided
- Generation commands included

✅ **Frontend Integration** (`docs/FRONTEND_AUTH_GUIDE.md`)
- Complete TypeScript/React examples
- Vue.js and Angular examples
- API client setup
- Custom hooks
- Error handling

---

## 🚀 Quick Enable (5 Minutes)

### Step 1: Copy Environment File

```bash
cp .env.example .env
```

### Step 2: Generate Secure Keys

```bash
# Generate API Key
openssl rand -hex 32

# Generate JWT Secret
openssl rand -base64 64
```

### Step 3: Update .env File

```bash
# Enable authentication
AUTH_ENABLED=true

# Add your generated API keys (use keys from Step 2)
API_KEYS=8a7b6c5d4e3f2a1b0c9d8e7f6a5b4c3d2e1f0a9b8c7d6e5f4a3b2c1d0e9f8a7b

# Add JWT secret (use secret from Step 2)
JWT_SECRET_KEY=your-generated-jwt-secret-here

# Set allowed origins (your frontend domains)
ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com
```

### Step 4: Update api_server.py (Add 3 Lines)

Add this at the top of `api_server.py` after other imports:

```python
# Add after existing imports (around line 20)
from core.security import setup_security

# Add after app = Flask(__name__) and before CORS(app)
# Replace:
# CORS(app)

# With:
setup_security(app)  # This replaces CORS and adds security
```

### Step 5: Restart API Server

```bash
python api_server.py
```

**Done!** Security is now enabled.

---

## 🔐 Adding Authentication to Endpoints

### Option 1: Protect All Endpoints (Recommended)

```python
# Add at the top of api_server.py
from core.auth import require_auth

# Apply to all routes after the route definition
@app.route('/api/scrape/start', methods=['POST'])
@require_auth  # Add this line
def start_scrape():
    # ... existing code
    pass
```

### Option 2: Protect Specific Endpoints

```python
from core.auth import require_auth, require_api_key, require_jwt

# Public endpoint - no auth required
@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy'})

# Protected with API key OR JWT
@app.route('/api/data/master', methods=['GET'])
@require_auth
def get_master_data():
    # ... existing code
    pass

# Protected with API key only
@app.route('/api/scrape/start', methods=['POST'])
@require_api_key
def start_scrape():
    # ... existing code
    pass

# Protected with JWT only (for user-specific actions)
@app.route('/api/searches', methods=['POST'])
@require_jwt
def create_search():
    user_id = request.user_id  # Available from JWT
    # ... existing code
    pass
```

### Option 3: Auto-Protect All Routes (Easiest)

Add this helper function to `api_server.py`:

```python
from core.auth import require_auth

def protect_all_routes(app):
    """Apply authentication to all /api/* routes except health"""

    @app.before_request
    def check_auth():
        # Skip auth for health check
        if request.path == '/api/health':
            return None

        # Skip auth for OPTIONS requests (CORS preflight)
        if request.method == 'OPTIONS':
            return None

        # Check if this is an API route
        if request.path.startswith('/api/'):
            # Manually run auth check
            from core.auth import AUTH_ENABLED, API_KEYS
            import jwt
            from core.auth import JWT_SECRET_KEY, JWT_ALGORITHM

            if not AUTH_ENABLED:
                return None

            # Try API key
            api_key = request.headers.get('X-API-Key')
            if api_key and api_key in API_KEYS:
                return None

            # Try JWT
            auth_header = request.headers.get('Authorization', '')
            if auth_header.startswith('Bearer '):
                token = auth_header.replace('Bearer ', '', 1)
                try:
                    payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
                    request.user_id = payload.get('user_id')
                    return None
                except:
                    pass

            # No valid auth
            return jsonify({
                'error': 'Authentication required',
                'message': 'Provide X-API-Key or Authorization: Bearer <token>'
            }), 401

# Call after app creation
protect_all_routes(app)
```

---

## 🌐 HTTPS Setup

### Development (Self-Signed Certificate)

```bash
# Generate self-signed certificate
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes

# Update api_server.py
if __name__ == '__main__':
    context = ('cert.pem', 'key.pem')
    app.run(host='0.0.0.0', port=5443, ssl_context=context)
```

### Production (Let's Encrypt - FREE)

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d yourdomain.com -d api.yourdomain.com

# Configure nginx
sudo nano /etc/nginx/sites-available/api
```

```nginx
# /etc/nginx/sites-available/api
server {
    listen 443 ssl;
    server_name api.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/api.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-Proto https;
    }
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name api.yourdomain.com;
    return 301 https://$server_name$request_uri;
}
```

```bash
# Enable site and restart nginx
sudo ln -s /etc/nginx/sites-available/api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Auto-renewal
sudo certbot renew --dry-run
```

---

## 🧪 Testing Security

### Test API Key Authentication

```bash
# Should fail (no API key)
curl http://localhost:5000/api/data/master

# Should succeed
curl -H "X-API-Key: your-api-key" \
  http://localhost:5000/api/data/master
```

### Test Security Headers

```bash
curl -I http://localhost:5000/api/health
```

Should see:
```
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Content-Security-Policy: default-src 'self'
```

### Test CORS

```bash
curl -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: GET" \
  -X OPTIONS http://localhost:5000/api/health
```

---

## 📋 Security Checklist

### Before Enabling in Production

- [ ] Generated strong API keys
- [ ] Generated strong JWT secret
- [ ] Updated .env file (never commit!)
- [ ] Set AUTH_ENABLED=true
- [ ] Set ALLOWED_ORIGINS to your actual domains
- [ ] Applied authentication to routes
- [ ] Tested authentication locally
- [ ] Set up HTTPS (Let's Encrypt)
- [ ] Configured nginx reverse proxy
- [ ] Tested HTTPS works
- [ ] Set up auto-renewal for certificates
- [ ] Verified security headers
- [ ] Tested CORS from frontend
- [ ] Updated frontend with API keys
- [ ] Deployed to production
- [ ] Monitored logs for auth failures

---

## 🔄 Maintenance

### Rotating API Keys

```bash
# 1. Generate new key
openssl rand -hex 32

# 2. Add to .env (keep old one temporarily)
API_KEYS=old-key,new-key

# 3. Update frontend to use new key
# 4. After frontend deployed, remove old key
API_KEYS=new-key

# 5. Restart API server
```

### Monitoring

```bash
# Check authentication failures
tail -f logs/scraper.log | grep "Authentication failed"

# Check rate limits
tail -f logs/scraper.log | grep "Rate limit exceeded"
```

---

## 🎯 Summary

**What You Get:**

✅ API Key Authentication - Simple, ready to use
✅ JWT Authentication - For user-based apps
✅ Security Headers - XSS, Clickjacking protection
✅ CORS Protection - Only allowed origins
✅ Input Validation - Sanitization functions ready
✅ Path Traversal Protection - File access secured
✅ Error Handling - No information leakage
✅ Rate Limiting - Built-in protection

**How to Enable:**

1. Copy `.env.example` to `.env`
2. Set `AUTH_ENABLED=true`
3. Add 1 line to `api_server.py`: `setup_security(app)`
4. Restart server

**That's it!** Security is production-ready.

---

**Files to Review:**
- `core/auth.py` - Authentication system
- `core/security.py` - Security middleware
- `.env.example` - Configuration template
- `docs/FRONTEND_AUTH_GUIDE.md` - Frontend integration

---

**Status:** ✅ Implemented, Ready to Enable
**Effort:** 5 minutes to enable
**Impact:** Production-grade security
