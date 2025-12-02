#!/bin/bash
# Setup script for Crypto Scalping Trading Bot

echo "Crypto Scalping Trading Bot - Environment Setup"
echo "==================================="
echo ""

# Check if .env exists
if [ -f .env ]; then
    echo "Warning: .env file already exists. Backing up to .env.backup"
    cp .env .env.backup
fi

# Create .env from template
cat > .env << 'EOF'
# Environment
ENVIRONMENT=development

# Coinbase API Credentials
COINBASE_API_KEY=
COINBASE_API_SECRET=
COINBASE_API_PASSPHRASE=

# Database Settings
DB_HOST=localhost
DB_PORT=5432
DB_NAME=tradingbot
DB_USER=postgres
DB_PASSWORD=

# Trading Mode
PAPER_TRADING=true

# Alert Settings (Optional)
SLACK_WEBHOOK_URL=
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=

# Logging
LOG_LEVEL=INFO
EOF

echo ".env file created successfully!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your configuration"
echo "2. Create PostgreSQL database: createdb tradingbot"
echo "3. Install dependencies: pip install -r requirements.txt"
echo "4. Run the bot: python main.py"
