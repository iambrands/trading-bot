# Claude AI Integration Setup Guide

## Quick Setup

### 1. Get Claude API Key

1. Visit: https://console.anthropic.com/
2. Sign up or log in
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key

### 2. Add to Environment

Add to your `.env` file:

```env
# Claude AI Configuration
CLAUDE_API_KEY=your_api_key_here
CLAUDE_MODEL=claude-3-5-sonnet-20241022
```

### 3. Restart Bot

```bash
# Stop the bot (Ctrl+C)
# Restart it
python main.py
```

---

## Features Available with AI

### 1. Market Analysis
- Navigate to **Market Conditions** page
- Click **"🤖 Get AI Analysis"** button
- Get intelligent insights about:
  - Current market conditions
  - Trading opportunities
  - Risk assessment
  - Actionable recommendations

### 2. Strategy Explanation
- AI can explain how your strategy works
- Understand performance metrics
- Get suggestions for improvement

### 3. User Guidance
- Ask questions about the bot
- Get help understanding features
- Learn best practices

---

## Usage Examples

### Market Analysis:
1. Go to Market Conditions page
2. Review current conditions
3. Click "🤖 Get AI Analysis"
4. Read AI insights and recommendations

### Get Help:
- AI can answer questions like:
  - "How does the EMA strategy work?"
  - "Why aren't trades executing?"
  - "What do these metrics mean?"
  - "How should I configure my strategy?"

---

## Cost Information

- Claude API pricing: https://www.anthropic.com/pricing
- Usage is minimal (only when you click the button)
- No automatic AI calls (you control when it runs)

---

## Troubleshooting

**AI button shows error:**
- Check that `CLAUDE_API_KEY` is set in `.env`
- Verify API key is valid
- Restart the bot after adding the key

**AI not responding:**
- Check internet connection
- Verify API key has credits
- Check bot logs for errors

**AI features work without API key:**
- Yes! All features work fine
- AI features will show a message to configure the key
- Core bot functionality is unaffected

---

## Notes

- AI is completely optional
- Bot works perfectly without AI
- AI only runs when you request it
- All data stays private (sent to Claude API for analysis only)

---

**Enjoy your AI-powered trading assistant!** 🤖

