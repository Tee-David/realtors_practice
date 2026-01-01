# Firebase Authentication Setup Guide

This guide walks you through setting up Firebase Authentication for the Realtors' Practice application.

---

## Overview

The authentication system uses:
- **Backend**: Firebase Admin SDK (Python) + Flask API
- **Frontend**: Firebase Client SDK (JavaScript/TypeScript) + Next.js
- **Features**: Email/password authentication, user management, role-based access control

---

## Prerequisites

✅ Firebase project already created: **realtor-s-practice**
✅ Firebase Admin SDK credentials: `backend/realtor-s-practice-firebase-adminsdk-fbsvc-3071684e9a.json`
✅ Firebase SDK installed in frontend: `npm install firebase` (completed)

---

## Step 1: Enable Authentication in Firebase Console

1. Go to [Firebase Console](https://console.firebase.google.com/project/realtor-s-practice)
2. Click **Authentication** in the left sidebar
3. Click **Get Started** (if not already enabled)
4. Go to **Sign-in method** tab
5. Enable **Email/Password** provider:
   - Click on "Email/Password"
   - Toggle "Enable" to ON
   - Toggle "Email link (passwordless sign-in)" if desired
   - Click "Save"

---

## Step 2: Get Firebase Web App Configuration

1. In Firebase Console, click the **gear icon** (⚙️) next to "Project Overview"
2. Select **Project settings**
3. Scroll down to **Your apps** section
4. If you don't have a web app:
   - Click **Add app** button
   - Select **Web** (</> icon)
   - Enter app nickname: "Realtors Practice Web"
   - Check "Also set up Firebase Hosting" (optional)
   - Click **Register app**
5. Copy the `firebaseConfig` object
6. Create `frontend/.env.local` file with these values:

```env
NEXT_PUBLIC_FIREBASE_API_KEY=your-api-key-here
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=realtor-s-practice.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=realtor-s-practice
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=realtor-s-practice.appspot.com
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=your-sender-id-here
NEXT_PUBLIC_FIREBASE_APP_ID=your-app-id-here
NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID=your-measurement-id-here
NEXT_PUBLIC_API_URL=http://localhost:5000
```

---

## Step 3: Test Backend Authentication

### Start the API Server

```bash
cd backend
python api_server.py
```

### Test Authentication Endpoints

```bash
# Health check
curl http://localhost:5000/api/auth/health

# Expected response:
# {
#   "status": "healthy",
#   "service": "authentication",
#   "firebase_initialized": true,
#   "timestamp": "2026-01-01T..."
# }
```

### Register a Test User

```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123",
    "displayName": "Test User"
  }'

# Expected response:
# {
#   "success": true,
#   "message": "User registered successfully",
#   "user": {...},
#   "customToken": "..."
# }
```

---

## Step 4: Update Frontend to Use Authentication

### Add AuthProvider to Your App

Edit `frontend/app/layout.tsx`:

```typescript
import { AuthProvider } from '@/contexts/AuthContext';

export default function RootLayout({ children }: { children: React.Node }) {
  return (
    <html>
      <body>
        <AuthProvider>
          {children}
        </AuthProvider>
      </body>
    </html>
  );
}
```

### Use Authentication in Components

```typescript
'use client';

import { useAuth } from '@/contexts/AuthContext';

export function MyComponent() {
  const { user, signIn, signUp, logout } = useAuth();

  const handleSignIn = async () => {
    const result = await signIn('user@example.com', 'password123');
    if (result.success) {
      console.log('Signed in!', result.user);
    } else {
      console.error('Sign in failed:', result.error);
    }
  };

  return (
    <div>
      {user ? (
        <>
          <p>Welcome, {user.displayName || user.email}!</p>
          <button onClick={logout}>Logout</button>
        </>
      ) : (
        <button onClick={handleSignIn}>Sign In</button>
      )}
    </div>
  );
}
```

---

## Step 5: Integrate with Existing User Management

### Replace Mock Data with Real Firebase Users

Edit `frontend/components/user/user-management.tsx`:

```typescript
import { useAuthAPI } from '@/hooks/useAuthAPI';
import { useAuth } from '@/contexts/AuthContext';

export function UserManagement() {
  const { isAdmin } = useAuth();
  const { listUsers, updateUserRole, deleteUser } = useAuthAPI();
  const [users, setUsers] = useState([]);

  useEffect(() => {
    if (isAdmin) {
      loadUsers();
    }
  }, [isAdmin]);

  const loadUsers = async () => {
    const result = await listUsers(100);
    if (result.success) {
      setUsers(result.data.users);
    }
  };

  const handleRoleChange = async (uid: string, newRole: 'admin' | 'user') => {
    const result = await updateUserRole(uid, newRole);
    if (result.success) {
      loadUsers(); // Reload users
    }
  };

  // ... rest of component
}
```

---

## Step 6: Configure CORS for Production

When deploying to production, update CORS settings:

**Backend** (`backend/core/security.py` - already configured):
```python
# Update allowed origins
ALLOWED_ORIGINS=https://your-production-domain.com,https://your-vercel-app.vercel.app
```

**Frontend** (Vercel environment variables):
```env
NEXT_PUBLIC_API_URL=https://your-backend-url.com
```

---

## Security Checklist

Before going to production, ensure:

- [ ] Email/Password authentication is enabled in Firebase Console
- [ ] Firebase web app configuration is set in `frontend/.env.local`
- [ ] Backend API is accessible at the URL specified in `NEXT_PUBLIC_API_URL`
- [ ] CORS is properly configured for your production domains
- [ ] Service account credentials are secure (not committed to git)
- [ ] Environment variables are set in production deployment (Vercel, Render, etc.)
- [ ] SSL/HTTPS is enabled for both frontend and backend
- [ ] Password reset emails are configured (Firebase Email Templates)
- [ ] Admin users are properly assigned (via `updateUserRole` endpoint)

---

## API Endpoints

### Public Endpoints (No Auth Required)

```bash
POST /api/auth/register          # Register new user
POST /api/auth/verify-token      # Verify Firebase ID token
POST /api/auth/password-reset    # Request password reset
GET  /api/auth/health            # Health check
```

### Protected Endpoints (Requires Authentication)

```bash
GET    /api/auth/user/me         # Get current user
PUT    /api/auth/user/me         # Update current user
GET    /api/auth/user/<uid>      # Get user by ID (admin or self)
DELETE /api/auth/user/<uid>      # Delete user (admin or self)
GET    /api/auth/users           # List all users (admin only)
PUT    /api/auth/user/<uid>/role # Update user role (admin only)
POST   /api/auth/logout          # Logout (revoke tokens)
```

### Authentication Header Format

```bash
Authorization: Bearer <firebase-id-token>
```

---

## Common Issues & Solutions

### Issue: "firebase_initialized": false

**Solution**: Check that `FIREBASE_SERVICE_ACCOUNT` environment variable points to the correct credentials file:

```bash
cd backend
export FIREBASE_SERVICE_ACCOUNT="realtor-s-practice-firebase-adminsdk-fbsvc-3071684e9a.json"
python api_server.py
```

### Issue: CORS errors in frontend

**Solution**: Ensure backend is running and CORS is properly configured. Check `backend/core/security.py` and verify `ALLOWED_ORIGINS`.

### Issue: "No authentication token available"

**Solution**: Ensure user is signed in and Firebase is properly initialized in frontend. Check browser console for Firebase errors.

### Issue: Token expired

**Solution**: Firebase tokens expire after 1 hour. The SDK automatically refreshes them. If issues persist, sign out and sign in again.

---

## Testing with Playwright

You can test the authentication flow with Playwright:

```typescript
import { test, expect } from '@playwright/test';

test('user can sign up and sign in', async ({ page }) => {
  // Navigate to app
  await page.goto('http://localhost:3000');

  // Click sign up
  await page.click('[data-testid="sign-up-button"]');

  // Fill registration form
  await page.fill('[name="email"]', 'test@example.com');
  await page.fill('[name="password"]', 'password123');
  await page.fill('[name="displayName"]', 'Test User');

  // Submit
  await page.click('[type="submit"]');

  // Verify signed in
  await expect(page.locator('[data-testid="user-menu"]')).toBeVisible();
});
```

---

## Next Steps

1. ✅ Enable Email/Password authentication in Firebase Console
2. ✅ Get Firebase web app configuration
3. ✅ Create `frontend/.env.local` with Firebase config
4. ✅ Test backend authentication endpoints
5. ✅ Add AuthProvider to frontend app
6. ✅ Replace mock user management with real Firebase users
7. ✅ Test end-to-end authentication flow
8. ✅ Configure production CORS and environment variables

---

## Files Created

### Backend
- `backend/core/firebase_auth.py` - Firebase Auth manager
- `backend/api/routes/auth_routes.py` - Authentication API routes
- `backend/api_server.py` - Updated to register auth routes

### Frontend
- `frontend/lib/firebase/config.ts` - Firebase initialization
- `frontend/lib/firebase/auth.ts` - Authentication helper functions
- `frontend/contexts/AuthContext.tsx` - Auth context and provider
- `frontend/hooks/useAuthAPI.ts` - Backend API integration hooks
- `frontend/.env.example` - Environment variable template

### Documentation
- `FIREBASE_AUTH_SETUP.md` - This file

---

## Support

For issues or questions:
- Firebase Documentation: https://firebase.google.com/docs/auth
- Firebase Console: https://console.firebase.google.com/project/realtor-s-practice
- Backend API Docs: `backend/docs/FOR_FRONTEND_DEVELOPER.md`

---

**Last Updated**: 2026-01-01
**Version**: 1.0.0
**Status**: Implementation Complete ✅
