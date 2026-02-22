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
    # Primary Exchange Selection (binance or coinbase)
    EXCHANGE = os.getenv('EXCHANGE', 'coinbase').lower()  # Default to coinbase for backward compatibility
    
    # Coinbase Settings (LEGACY - High fees 0.6%)
    COINBASE_API_KEY = os.getenv('COINBASE_API_KEY', '')
    COINBASE_API_SECRET = os.getenv('COINBASE_API_SECRET', '')
    COINBASE_API_PASSPHRASE = os.getenv('COINBASE_API_PASSPHRASE', '')
    COINBASE_API_URL = 'https://api.coinbase.com/api/v3/brokerage'
    COINBASE_WS_URL = 'wss://advanced-trade-ws.coinbase.com'
    
    # Binance Settings (RECOMMENDED - Low fees 0.1%)
    BINANCE_API_KEY = os.getenv('BINANCE_API_KEY', '')
    BINANCE_API_SECRET = os.getenv('BINANCE_API_SECRET', '')
    BINANCE_TESTNET = os.getenv('BINANCE_TESTNET', 'true').lower() == 'true'  # Start with testnet
    
    # Trading Pairs
    # Default trading pairs - includes all pairs user has configured
    TRADING_PAIRS: List[str] = [
        'BTC-USD', 
        'ETH-USD', 
        'SOL-USD', 
        'ADA-USD', 
        'AVAX-USD', 
        'XRP-USD', 
        'DOGE-USD', 
        'MINA-USD', 
        'TRUMP-USD'
    ]
    
    # Account Settings
    ACCOUNT_SIZE = 100000.0  # $100,000
    
    # Risk Parameters
    RISK_PER_TRADE_PCT = 0.25  # 0.25% per trade
    MAX_POSITIONS = 2  # Maximum simultaneous positions
    DAILY_LOSS_LIMIT = 2000.0  # $2,000 daily loss limit
    MAX_POSITION_SIZE_PCT = 2.0  # 2% of account max per position (conservative for scalping)
    MAX_POSITION_SIZE_USDT = 500.0  # Hard cap: $500 max per trade (prevents oversized positions)
    POSITION_TIMEOUT_MINUTES = 10  # 10 minutes max hold time
    
    # Strategy Marketplace
    ACTIVE_STRATEGY_ID = os.getenv('ACTIVE_STRATEGY_ID', 'ema_rsi')  # ema_rsi, rsi_only, bollinger

    # Strategy Parameters
    EMA_PERIOD = 50  # EMA(50)
    RSI_PERIOD = 14  # RSI(14)
    VOLUME_PERIOD = 20  # 20-period volume average
    # RELAXED: Previous settings (vol 1.2x, RSI 50-75/25-50) generated 0 trades in 30+ days
    VOLUME_MULTIPLIER = 0.9  # 0.9x - allow below-avg volume (crypto often has low vol candles)
    RSI_LONG_MIN = 45   # Widen from 50 - capture more uptrend entries
    RSI_LONG_MAX = 80   # Widen from 75 - RSI often 75-80 in strong trends
    RSI_SHORT_MIN = 20  # Widen from 25 - capture more downtrend entries
    RSI_SHORT_MAX = 55  # Widen from 50 - RSI often 45-55 in pullbacks
    MIN_CONFIDENCE_SCORE = 60  # Lower from 65 - balance quality vs. frequency
    
    # Exit Parameters - OPTIMIZED FOR COINBASE (works for Binance too)
    # Coinbase fees: 1.2% round trip - TP must exceed this for net profit
    # Binance fees: 0.2% round trip - same TP yields even better net
    TAKE_PROFIT_MIN = 1.50  # 1.5% min (Coinbase: ~0.3% net | Binance: ~1.3% net)
    TAKE_PROFIT_MAX = 2.00  # 2.0% max (Coinbase: ~0.8% net | Binance: ~1.8% net)
    STOP_LOSS_MIN = 0.50   # 0.5% min
    STOP_LOSS_MAX = 0.75   # 0.75% max
    TRAILING_STOP_ENABLED = False
    TRAILING_STOP_PCT = 0.5  # Exit when price reverses this % from best price
    TRAILING_STOP_ACTIVATION_PCT = 0.3  # Start trailing after price moved this % in favor (optional)
    
    # Fee Configuration
    VALIDATE_FEES_BEFORE_TRADE = True  # Validate profitability after fees
    MIN_PROFIT_AFTER_FEES = 0.25  # Minimum 0.25% net profit after fees
    
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
    PAPER_FEE_RATE = 0.006  # 0.6% fee (Coinbase - for backward compatibility)
    
    # Order Execution Settings
    ORDER_TYPE = os.getenv('ORDER_TYPE', 'limit').lower()  # 'limit' or 'market' - use limit for maker fees
    LIMIT_ORDER_OFFSET_PCT = 0.02  # Place limit orders 0.02% inside spread (for maker rebates)
    ORDER_TIMEOUT_SECONDS = 30  # Cancel unfilled limit orders after 30 seconds
    USE_POST_ONLY = True  # Maker orders only (lower fees on Binance)
    
    # Alert Settings
    SLACK_WEBHOOK_URL = os.getenv('SLACK_WEBHOOK_URL', '')
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
    TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')
    
    # AI Settings (Claude AI)
    # Strip whitespace and remove quotes if present (Railway sometimes adds quotes)
    # AI Configuration - OpenAI (Primary)
    _openai_key = os.getenv('OPENAI_API_KEY', '').strip()
    OPENAI_API_KEY = _openai_key.strip('"').strip("'") if _openai_key else ''
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')  # Default to gpt-4o-mini (cost-effective)
    
    # AI Configuration - Claude (Legacy, optional)
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

    # TradingView Webhook
    TRADINGVIEW_WEBHOOK_SECRET = os.getenv('TRADINGVIEW_WEBHOOK_SECRET', '').strip().strip('"').strip("'")
    TRADINGVIEW_ORDER_SIZE_USD = float(os.getenv('TRADINGVIEW_ORDER_SIZE_USD', '50'))


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
    import sys
    print("    get_config() entered", file=sys.stderr, flush=True)
    
    print("    Reading ENVIRONMENT env var...", file=sys.stderr, flush=True)
    env = os.getenv('ENVIRONMENT', 'development').lower()
    print(f"    ENVIRONMENT = {env}", file=sys.stderr, flush=True)
    
    if env == 'production':
        print("    Instantiating ProductionConfig...", file=sys.stderr, flush=True)
        try:
            config = ProductionConfig()
            print("    ✅ ProductionConfig created", file=sys.stderr, flush=True)
            return config
        except Exception as e:
            print(f"    ❌ ProductionConfig instantiation FAILED: {e}", file=sys.stderr, flush=True)
            import traceback
            traceback.print_exc(file=sys.stderr)
            raise
    else:
        print("    Instantiating DevelopmentConfig...", file=sys.stderr, flush=True)
        try:
            config = DevelopmentConfig()
            print("    ✅ DevelopmentConfig created", file=sys.stderr, flush=True)
            return config
        except Exception as e:
            print(f"    ❌ DevelopmentConfig instantiation FAILED: {e}", file=sys.stderr, flush=True)
            import traceback
            traceback.print_exc(file=sys.stderr)
            raise
    
    print("    get_config() completed", file=sys.stderr, flush=True)
