# Crypto Scalping Trading Bot - Authentication System

## Overview

Crypto Scalping Trading Bot now includes a complete JWT-based authentication system with:
- Beautiful landing page
- User signup and signin
- Protected dashboard routes
- Secure password hashing with bcrypt
- JWT token-based authentication

## Features

### Landing Page (`/landing`)
- Modern, responsive design
- Hero section with key features
- Feature cards highlighting bot capabilities
- Call-to-action buttons
- Smooth navigation

### Authentication
- **Sign Up** (`/signup`): Create new user accounts
- **Sign In** (`/signin`): Login to existing accounts
- **JWT Tokens**: 24-hour expiration, stored securely
- **Password Security**: Bcrypt hashing with salt

### Protected Routes
- Dashboard and all API endpoints require authentication
- Automatic redirect to landing page if not authenticated
- Token validation on every request

## Installation

### 1. Install New Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- `PyJWT==2.8.0` - JWT token handling
- `bcrypt==4.1.2` - Password hashing

### 2. Database Migration

The database schema has been updated automatically. The `users` table will be created when you run the bot.

### 3. Environment Variables (Optional)

Add to your `.env` file for production:

```env
JWT_SECRET_KEY=your_very_secure_secret_key_here
```

If not set, a random key will be generated (not recommended for production).

## Usage

### First-Time Setup

1. **Start the bot:**
   ```bash
   python main.py
   ```

2. **Visit the landing page:**
   - Navigate to `http://localhost:4000/landing`
   - Or go to `http://localhost:4000/` (will redirect if not authenticated)

3. **Create an account:**
   - Click "Get Started" or "Sign Up"
   - Fill in your details:
     - Full Name
     - Email Address
     - Password (minimum 8 characters)
     - Confirm Password
   - Click "Create Account"

4. **Access Dashboard:**
   - After signup, you'll be automatically logged in
   - You'll be redirected to the dashboard at `/`

### Signing In

1. Go to `http://localhost:4000/signin`
2. Enter your email and password
3. Click "Sign In"
4. You'll be redirected to the dashboard

### Logging Out

- Click the "🚪 Logout" link in the navigation bar
- You'll be redirected to the landing page
- Your session token will be cleared

## API Endpoints

### Public Endpoints

- `POST /api/auth/signup` - Create new user account
- `POST /api/auth/signin` - Authenticate user
- `GET /api/auth/verify` - Verify token validity

### Protected Endpoints

All other API endpoints require authentication:
- Include `Authorization: Bearer <token>` header, OR
- Token is automatically sent via HTTP-only cookie

### Signup Request

```json
POST /api/auth/signup
{
  "email": "user@example.com",
  "password": "securepassword123",
  "full_name": "John Doe"
}
```

**Response:**
```json
{
  "message": "User created successfully",
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "full_name": "John Doe"
  }
}
```

### Signin Request

```json
POST /api/auth/signin
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response:**
```json
{
  "message": "Signed in successfully",
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "full_name": "John Doe"
  }
}
```

## Security Features

1. **Password Hashing**: All passwords are hashed using bcrypt with automatic salt generation
2. **JWT Tokens**: Secure token-based authentication with expiration
3. **HTTP-Only Cookies**: Tokens stored in secure, HTTP-only cookies (prevents XSS)
4. **Token Validation**: Every protected route validates the token
5. **Automatic Redirects**: Unauthenticated users redirected to landing page

## Database Schema

### Users Table

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);
```

### Updated Trades Table

Trades now include a `user_id` foreign key to associate trades with users:

```sql
user_id INTEGER REFERENCES users(id) ON DELETE CASCADE
```

## Frontend Changes

### Dashboard Updates

- Added logout button in navigation
- Automatic token inclusion in API requests
- Redirect to landing page on 401 errors
- Token stored in localStorage for client-side access

### New Pages

- `/landing` - Landing page
- `/signup` - Sign up page
- `/signin` - Sign in page

## Troubleshooting

### "Database not initialized" error

Make sure the database is running and the bot can connect:

```bash
# Check PostgreSQL is running
psql -U your_user -d tradingbot -c "SELECT 1;"
```

### "Authentication required" error

- Make sure you're signed in
- Check that your token hasn't expired (24 hours)
- Try logging out and logging back in

### Token not being sent

- Check browser console for errors
- Ensure localStorage is enabled
- Try clearing cookies and localStorage

## Production Considerations

1. **Set JWT_SECRET_KEY**: Use a strong, random secret key in production
2. **HTTPS**: Always use HTTPS in production to protect tokens
3. **Token Expiration**: Consider shorter expiration times for production
4. **Rate Limiting**: Implement rate limiting on auth endpoints
5. **Email Verification**: Consider adding email verification for signups

## File Structure

```
TradingBot/
├── auth/
│   ├── __init__.py
│   └── auth_manager.py          # JWT & password handling
├── static/
│   ├── landing.html             # Landing page
│   ├── landing.css              # Landing page styles
│   ├── signup.html              # Signup page
│   ├── signin.html              # Signin page
│   ├── auth.css                 # Auth pages styles
│   └── auth.js                  # Auth frontend logic
├── database/
│   └── db_manager.py            # Updated with user methods
└── api/
    └── rest_api.py              # Updated with auth endpoints
```

## Next Steps

Consider adding:
- Email verification
- Password reset functionality
- Two-factor authentication
- User profile management
- API key management per user

