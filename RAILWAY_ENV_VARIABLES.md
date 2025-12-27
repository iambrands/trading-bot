# Railway Environment Variables Setup

## ✅ Required Variables

### 1. JWT_SECRET_KEY (CRITICAL)
**Required for authentication to work**

Generate a secure key:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Add to Railway:
- Go to Railway Dashboard → Your Service → Variables
- Add: `JWT_SECRET_KEY` = `<generated-key>`

### 2. Database Configuration
**Railway automatically provides `DATABASE_URL` when you add PostgreSQL**

The app will use Railway's `DATABASE_URL` automatically (already configured in `config.py`).

If you need individual variables instead:
- `DB_HOST`
- `DB_PORT` 
- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`

### 3. Environment Settings
```
ENVIRONMENT=production
PAPER_TRADING=true  # Set to false for live trading
LOG_LEVEL=INFO
```

## ⚠️ Important Optional Variables

### Coinbase API (Only if using live trading)
```
COINBASE_API_KEY=<your-api-key>
COINBASE_API_SECRET=<your-api-secret>
COINBASE_API_PASSPHRASE=<your-passphrase>
```

### AI Features (Claude AI)
```
CLAUDE_API_KEY=<your-claude-api-key>
CLAUDE_MODEL=claude-3-haiku-20240307
```

### Alert Notifications (Optional)
```
SLACK_WEBHOOK_URL=<your-slack-webhook>
TELEGRAM_BOT_TOKEN=<your-bot-token>
TELEGRAM_CHAT_ID=<your-chat-id>
```

## 🚀 Quick Setup Steps

1. **Generate JWT Secret Key:**
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

2. **In Railway Dashboard:**
   - Go to your service
   - Click "Variables" tab
   - Add these variables:

   ```
   JWT_SECRET_KEY=<paste-generated-key>
   ENVIRONMENT=production
   PAPER_TRADING=true
   LOG_LEVEL=INFO
   ```

3. **Add PostgreSQL Database:**
   - In Railway project, click "+ New"
   - Select "Database" → "PostgreSQL"
   - Railway automatically sets `DATABASE_URL`

4. **Optional: Add API Keys** (if you have them):
   - Coinbase API keys (for live trading)
   - Claude API key (for AI features)

## ✅ Minimum Required for Testing

For the app to work and allow login/signup:
- ✅ `JWT_SECRET_KEY` (required)
- ✅ Database (Railway auto-provides `DATABASE_URL`)
- ✅ `ENVIRONMENT=production` (recommended)
- ✅ `PAPER_TRADING=true` (safe for testing)

Everything else is optional and can be added later.

## 🔍 Verify Setup

After adding variables:
1. Railway will automatically redeploy
2. Check logs to verify app starts
3. Visit your Railway URL
4. Try signing up/logging in

## ⚠️ Security Notes

- **Never commit** `.env` files or API keys to Git
- Use Railway's Variables interface (secure)
- Generate a new `JWT_SECRET_KEY` for production
- Keep API keys private

