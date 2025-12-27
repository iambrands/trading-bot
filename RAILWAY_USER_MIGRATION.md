# Migrate User Credentials to Railway

## Option 1: Use Migration Script (Recommended)

The script will copy your user account from localhost to Railway, preserving your password.

### Steps:

1. **Get Railway DATABASE_URL:**
   - Go to Railway Dashboard → Your Project → PostgreSQL Database
   - Click on the database service
   - Go to "Variables" tab
   - Copy the `DATABASE_URL` value

2. **Run the migration script:**
   ```bash
   python migrate_user_to_railway.py
   ```

3. **Follow the prompts:**
   - Enter your email address
   - Paste the Railway DATABASE_URL when prompted
   - Confirm the migration

The script will:
- ✅ Find your user in localhost database
- ✅ Copy your password hash to Railway database
- ✅ Preserve your email, full name, and settings

## Option 2: Sign Up Again (Simpler)

If you prefer, you can just sign up again on Railway:

1. Visit: `https://web-production-f8308.up.railway.app/signup`
2. Use the same email and password you use on localhost
3. Done!

This creates a fresh account but uses the same credentials.

## Option 3: Manual Database Insert

If you want to manually insert the user:

1. **Get password hash from localhost:**
   ```bash
   psql -U postgres -d tradingbot -c "SELECT email, password_hash FROM users WHERE email='your-email@example.com';"
   ```

2. **Connect to Railway database** (using Railway's database connection info)

3. **Insert the user:**
   ```sql
   INSERT INTO users (email, password_hash, full_name, is_active)
   VALUES ('your-email@example.com', '<password-hash-from-localhost>', 'Your Name', true);
   ```

## Which Option Should You Use?

- **Option 1 (Migration Script)**: Best if you want to preserve your exact account and any existing data
- **Option 2 (Sign Up Again)**: Simplest, but creates a new account ID
- **Option 3 (Manual)**: Advanced, if you need more control

**Recommendation**: Use Option 1 (migration script) if you want to keep the same user ID and data, or Option 2 (sign up) if you just want to log in with the same credentials.

