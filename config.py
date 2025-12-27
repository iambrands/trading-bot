"""Configuration management for TradePilot."""

import os
from typing import List
from urllib.parse import urlparse
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration with all default settings."""
    
    # Environment
    ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')
    
    # Exchange Settings
    COINBASE_API_KEY = os.getenv('COINBASE_API_KEY', '')
    COINBASE_API_SECRET = os.getenv('COINBASE_API_SECRET', '')
    COINBASE_API_PASSPHRASE = os.getenv('COINBASE_API_PASSPHRASE', '')
    COINBASE_API_URL = 'https://api.coinbase.com/api/v3/brokerage'
    COINBASE_WS_URL = 'wss://advanced-trade-ws.coinbase.com'
    
    # Trading Pairs
    TRADING_PAIRS: List[str] = ['BTC-USD', 'ETH-USD']
    
    # Account Settings
    ACCOUNT_SIZE = 100000.0  # $100,000
    
    # Risk Parameters
    RISK_PER_TRADE_PCT = 0.25  # 0.25% per trade
    MAX_POSITIONS = 2  # Maximum simultaneous positions
    DAILY_LOSS_LIMIT = 2000.0  # $2,000 daily loss limit
    MAX_POSITION_SIZE_PCT = 50.0  # 50% of account max per position
    POSITION_TIMEOUT_MINUTES = 10  # 10 minutes max hold time
    
    # Strategy Parameters
    EMA_PERIOD = 50  # EMA(50)
    RSI_PERIOD = 14  # RSI(14)
    VOLUME_PERIOD = 20  # 20-period volume average
    VOLUME_MULTIPLIER = 1.5  # 1.5x average volume for confirmation
    RSI_LONG_MIN = 55  # Minimum RSI for long entry
    RSI_LONG_MAX = 70  # Maximum RSI for long entry
    RSI_SHORT_MIN = 30  # Minimum RSI for short entry
    RSI_SHORT_MAX = 45  # Maximum RSI for short entry
    MIN_CONFIDENCE_SCORE = 70  # Minimum confidence to trade (%)
    
    # Exit Parameters
    TAKE_PROFIT_MIN = 0.15  # 0.15% minimum take profit
    TAKE_PROFIT_MAX = 0.40  # 0.40% maximum take profit
    STOP_LOSS_MIN = 0.10  # 0.10% minimum stop loss
    STOP_LOSS_MAX = 0.50  # 0.50% maximum stop loss
    
    # Trading Loop Settings
    LOOP_INTERVAL_SECONDS = 5  # Check every 5 seconds
    
    # Database Settings
    # Support DATABASE_URL (Railway, Heroku) or individual variables
    _db_url = os.getenv('DATABASE_URL')
    if _db_url:
        # Parse DATABASE_URL (format: postgresql://user:password@host:port/dbname)
        _parsed = urlparse(_db_url)
        DB_HOST = _parsed.hostname or 'localhost'
        DB_PORT = _parsed.port or 5432
        DB_NAME = _parsed.path.lstrip('/') if _parsed.path else 'tradingbot'
        DB_USER = _parsed.username or 'postgres'
        DB_PASSWORD = _parsed.password or ''
    else:
        # Fallback to individual environment variables
        DB_HOST = os.getenv('DB_HOST', 'localhost')
        DB_PORT = int(os.getenv('DB_PORT', '5432'))
        DB_NAME = os.getenv('DB_NAME', 'tradingbot')
        DB_USER = os.getenv('DB_USER', 'postgres')
        DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    
    # API Server Settings
    API_HOST = '0.0.0.0'
    API_PORT = 4000
    CORS_ORIGINS = ['http://localhost:3000', 'http://localhost:8080']
    
    # Paper Trading
    PAPER_TRADING = os.getenv('PAPER_TRADING', 'true').lower() == 'true'
    USE_REAL_MARKET_DATA = os.getenv('USE_REAL_MARKET_DATA', 'true').lower() == 'true'
    PAPER_SLIPPAGE_MIN = 0.01  # 0.01% minimum slippage
    PAPER_SLIPPAGE_MAX = 0.05  # 0.05% maximum slippage
    PAPER_FEE_RATE = 0.006  # 0.6% fee (maker/taker)
    
    # Alert Settings
    SLACK_WEBHOOK_URL = os.getenv('SLACK_WEBHOOK_URL', '')
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
    TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')
    
    # AI Settings (Claude AI)
    # Strip whitespace and remove quotes if present (Railway sometimes adds quotes)
    _claude_key = os.getenv('CLAUDE_API_KEY', '').strip()
    CLAUDE_API_KEY = _claude_key.strip('"').strip("'") if _claude_key else ''
    CLAUDE_MODEL = os.getenv('CLAUDE_MODEL', 'claude-3-haiku-20240307')
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = 'tradingbot.log'
    
    # Performance Targets
    TARGET_WIN_RATE = 55.0  # >55%
    TARGET_PROFIT_FACTOR = 1.5  # >1.5
    TARGET_SHARPE_RATIO = 1.5  # >1.5
    TARGET_MAX_DRAWDOWN = 5.0  # <5%
    
    # JWT Authentication
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', '')
    JWT_ALGORITHM = 'HS256'
    JWT_EXPIRY_HOURS = 24


class DevelopmentConfig(Config):
    """Development configuration with paper trading and debug logging."""
    
    ENVIRONMENT = 'development'
    PAPER_TRADING = True
    LOG_LEVEL = 'DEBUG'
    DEBUG = True


class ProductionConfig(Config):
    """Production configuration with live trading and optimized settings."""
    
    ENVIRONMENT = 'production'
    # IMPORTANT:
    # In production we default to live-trading behavior, but still allow explicitly enabling
    # paper trading via env var (e.g. Railway demo / user testing).
    PAPER_TRADING = os.getenv('PAPER_TRADING', 'false').lower() == 'true'
    LOG_LEVEL = 'WARNING'
    DEBUG = False
    LOOP_INTERVAL_SECONDS = 3  # Faster in production


def get_config() -> Config:
    """Get configuration based on environment."""
    env = os.getenv('ENVIRONMENT', 'development').lower()
    
    if env == 'production':
        return ProductionConfig()
    else:
        return DevelopmentConfig()
