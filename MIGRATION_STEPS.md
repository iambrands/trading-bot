# Migration Steps - Localhost to Railway

## Step-by-Step Instructions

### Step 1: Get Railway DATABASE_URL

1. Go to Railway Dashboard: https://railway.app/dashboard
2. Select your project (the one with `web-production-f8308`)
3. Click on the **PostgreSQL** database service (the one you added)
4. Click the **"Variables"** tab
5. Find `DATABASE_URL` - it should look like:
   ```
   postgresql://postgres:password@hostname:port/database
   ```
6. **Copy the entire DATABASE_URL** (you'll need to paste it when prompted)

### Step 2: Run the Migration Script

```bash
cd /Users/iabadvisors/TradingBot
python3 migrate_user_to_railway.py
```

### Step 3: Follow the Prompts

The script will ask you:
1. **Enter your email address** - Type the email you use to log in on localhost
2. **Enter Railway DATABASE_URL** - Paste the DATABASE_URL you copied in Step 1
3. **Confirm migration** - Type `y` to proceed

### Step 4: Verify Success

After the script completes, you should see:
```
✅ Migration complete!

You can now log in to Railway with:
  Email: your-email@example.com
  Password: (your original password)
```

### Step 5: Test Login

1. Visit: `https://web-production-f8308.up.railway.app`
2. Click "Sign In"
3. Enter your email and password (same as localhost)
4. You should be logged in!

## Troubleshooting

**If you get "User not found":**
- Double-check your email address
- Make sure you're using the exact email from localhost

**If you get database connection errors:**
- Verify the DATABASE_URL is correct
- Make sure Railway's PostgreSQL database is running
- Check that DATABASE_URL includes the full connection string

**If migration fails:**
- Check the error message
- Verify your localhost database is accessible
- Make sure you have the correct database credentials in your `.env` file

## Need Help?

If you encounter any issues, share the error message and I'll help you fix it!

