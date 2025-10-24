# RaptorFlow Frontend - OAuth Setup Guide

## Overview

Complete Google OAuth 2.0 integration for the RaptorFlow frontend with:
- Google OAuth login flow
- JWT token management
- Protected routes
- User session management
- Account/profile page
- Secure logout

## Files Created

### Context & State Management
- `context/AuthContext.tsx` - OAuth state management, token handling, user session
  - `AuthProvider` component wraps entire app
  - `useAuth()` hook for accessing auth state
  - Automatic token verification on app load
  - Token persistence via cookies

### Components
- `components/auth/GoogleLoginButton.tsx` - Google OAuth button
  - Integrates with Google OAuth library
  - Handles credential exchange with backend
  - Error handling and loading states
  - Automatic login via context

### Pages
- `app/auth/login/page.tsx` - Login page
  - Splendid UI with animations
  - Google OAuth integration
  - Auto-redirect to dashboard if logged in
  - Responsive design

- `app/dashboard/account/page.tsx` - Account settings
  - User profile information display
  - Security settings
  - Session management
  - Logout functionality

### Middleware & Layout
- `middleware.ts` - Route protection
  - Protects dashboard routes
  - Redirects unauthenticated users to login
  - Redirects authenticated users away from login
  - Public route configuration

- `app/auth/layout.tsx` - Auth layout
- `app/layout.tsx` - Updated with AuthProvider

### Configuration
- `.env.example` - Environment variables template

## Setup Instructions

### 1. Install Dependencies

```bash
cd frontend
npm install
```

New dependencies added:
- `@react-oauth/google` - Google OAuth library
- `axios` - HTTP client for API calls
- `js-cookie` - Secure cookie management

### 2. Configure Environment Variables

Copy and configure:
```bash
cp .env.example .env.local
```

Edit `.env.local`:
```env
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000

# Google OAuth Configuration
NEXT_PUBLIC_GOOGLE_CLIENT_ID=your-google-client-id-from-google-cloud

# Environment
NEXT_PUBLIC_ENVIRONMENT=development
```

### 3. Get Google OAuth Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select existing
3. Enable Google+ API
4. Create OAuth 2.0 credentials (Web application)
5. Add authorized redirect URIs:
   - `http://localhost:3000/auth/login` (development)
   - `http://localhost:3000/auth/callback` (development)
   - `https://yourdomain.com/auth/login` (production)
6. Copy Client ID to `.env.local`

### 4. Start Development Server

```bash
npm run dev
```

Access at `http://localhost:3000`

### 5. Test OAuth Flow

1. Visit `http://localhost:3000/auth/login`
2. Click "Sign in with Google"
3. Complete Google login
4. Should redirect to `/dashboard`
5. Visit `http://localhost:3000/dashboard/account` to view profile

## Usage

### In Components

```typescript
'use client'

import { useAuth } from '@/context/AuthContext'

export function MyComponent() {
  const { user, token, isAuthenticated, logout } = useAuth()

  if (!isAuthenticated) {
    return <p>Please login first</p>
  }

  return (
    <div>
      <h1>Welcome, {user?.name}</h1>
      <button onClick={logout}>Logout</button>
    </div>
  )
}
```

### Protecting Routes

Protected routes are automatically handled by `middleware.ts`:
- Any route under `/dashboard` requires authentication
- Unauthenticated users are redirected to `/auth/login`
- Logged-in users cannot access `/auth/login` (redirected to `/dashboard`)

### API Calls with Authentication

```typescript
import axios from 'axios'
import { useAuth } from '@/context/AuthContext'

export function DataComponent() {
  const { token } = useAuth()

  useEffect(() => {
    const fetchData = async () => {
      const response = await axios.get('/api/conversations', {
        headers: { Authorization: `Bearer ${token}` }
      })
    }
    fetchData()
  }, [token])
}
```

## API Endpoints Used

### Authentication
- `POST /api/auth/google/callback` - Exchange Google credential for JWT
- `POST /api/auth/verify-token` - Verify JWT token
- `POST /api/auth/logout` - Logout (backend cleanup)

## Features

✅ **Google OAuth 2.0 Integration**
- One-click login with Google account
- Automatic user/org creation on backend
- Secure credential exchange

✅ **Token Management**
- Automatic token persistence (secure cookies)
- Token verification on app load
- Automatic header injection with axios

✅ **Protected Routes**
- Middleware-based route protection
- Automatic redirects based on auth state
- Clean public route configuration

✅ **User Session**
- Auto-login on app load if token exists
- Graceful logout with backend sync
- Error handling and recovery

✅ **Beautiful UI**
- Animated login page
- Profile/account settings
- Responsive design
- Dark theme compatible

✅ **Type Safety**
- Full TypeScript support
- Exported interfaces for API responses
- Type-safe auth context

## Security Considerations

✅ **Token Security**
- JWT tokens stored in HttpOnly cookies (server-side)
- Automatic token refresh on verification
- Clear on logout

✅ **CORS**
- API calls through backend proxy
- Same-origin policy enforced

✅ **OAuth**
- Secure credential exchange via HTTPS
- State parameter for CSRF protection
- ID token validation on backend

✅ **Route Protection**
- Middleware validates auth on every request
- Server-side checks prevent unauthorized access

## Troubleshooting

### "Google Client ID is not configured"
- Make sure `NEXT_PUBLIC_GOOGLE_CLIENT_ID` is set in `.env.local`
- Restart development server after changing env vars

### Login fails with "Cannot reach API"
- Verify backend is running on `NEXT_PUBLIC_API_URL`
- Check CORS headers in backend config
- Check browser console for detailed error

### "Invalid token" errors
- Token may have expired (7-day cookie expiration)
- Visit login page again to get new token
- Check backend token validation logic

### Redirect loop on login
- Clear browser cookies: `auth_token`
- Check middleware public routes configuration
- Verify backend returns valid JWT

## Next Steps

1. **Email Login** - Add email/password authentication
2. **OAuth Providers** - Add GitHub, Microsoft OAuth
3. **2FA** - Two-factor authentication
4. **Profile Management** - Edit user profile, upload avatar
5. **Team Management** - Invite team members, manage roles

## References

- [React OAuth Google](https://www.npmjs.com/package/@react-oauth/google)
- [Next.js Middleware](https://nextjs.org/docs/advanced-features/middleware)
- [JWT Authentication](https://tools.ietf.org/html/rfc7519)
- [Google OAuth 2.0](https://developers.google.com/identity/protocols/oauth2)
