# Crypto Scalping Trading Bot - Project Overview

## 🎯 What We're Building

A **production-ready, automated cryptocurrency trading bot** that executes high-frequency scalping strategies on Coinbase Advanced Trade. The system includes a professional web dashboard, comprehensive risk management, and AI-powered market analysis.

---

## 🏗️ System Architecture

### **Backend (Python)**
- **Main Engine**: Automated trading bot that runs 24/7
- **REST API**: `aiohttp` web server for dashboard and control
- **Database**: PostgreSQL for trade history and performance metrics
- **Exchange Integration**: Coinbase Advanced Trade API client
- **Risk Management**: Position sizing, loss limits, safety controls
- **Strategy Engine**: EMA + RSI + Volume confirmation algorithm

### **Frontend (Web Dashboard)**
- **Multi-page SPA**: Overview, Positions, Trades, Performance, Portfolio, Charts, etc.
- **Progressive Web App (PWA)**: Installable on mobile devices
- **Real-time Updates**: Live price feeds, position tracking, performance metrics
- **Professional Charts**: TradingView-style candlestick charts with technical indicators
- **User Authentication**: JWT-based signup/signin system

---

## ✨ Core Features

### 1. **Automated Trading Engine**
- **Strategy**: EMA(50) + RSI(14) + Volume confirmation
- **Entry Conditions**: 
  - Long: Price > EMA, RSI 55-70, Volume > 1.5x average
  - Short: Price < EMA, RSI 30-45, Volume > 1.5x average
- **Exit Management**: Dynamic stop-loss (0.10-0.50%) and take-profit (0.15-0.40%)
- **Confidence Scoring**: Only trades when multiple signals align (≥70% confidence)

### 2. **Risk Management System**
- Position sizing based on 0.25% account risk
- Daily loss limit ($2,000 default)
- Maximum position limits (2 simultaneous positions)
- Position timeouts (10 min max hold time)
- Emergency kill switch
- Pre-trade validation checks

### 3. **Professional Web Dashboard**

#### **Dashboard Pages:**
- **Overview**: Bot status, balance, quick stats, recent activity
- **Market Conditions**: Real-time analysis of why trades aren't triggering
- **Positions**: Active positions with live P&L tracking
- **Trade History**: Complete audit trail with filters
- **Performance**: Win rate, profit factor, Sharpe ratio, drawdown analytics
- **Portfolio**: Asset allocation, pair statistics, tax reporting
- **Charts**: TradingView-style candlesticks with EMA, RSI, Volume indicators
- **Advanced Orders**: Trailing stops, OCO, bracket orders, iceberg orders
- **Grid Trading**: Automated buy/sell at multiple price levels
- **DCA (Dollar Cost Averaging)**: Systematic investment strategies
- **Settings**: Configure all strategy parameters
- **Logs**: System operation logs viewer

#### **Key Dashboard Features:**
- Real-time price updates (every 5 seconds)
- Interactive charts with multiple timeframes (1m, 5m, 15m, 1h, 4h, 1d)
- Mobile-responsive design
- PWA support (installable, offline-capable)
- Toast notifications for trade events
- Dark theme with gold accents

### 4. **Backtesting Engine**
- Test strategies on 30-90 days of historical data
- Performance metrics: ROI, win rate, profit factor, Sharpe ratio, drawdown
- AI-powered analysis of backtest results (Claude AI integration)
- Strategy optimization tools

### 5. **AI Market Analysis**
- Claude AI integration for real-time market insights
- Trading opportunity identification
- Risk assessment and recommendations
- Backtest result analysis

### 6. **Advanced Order Types**
- **Trailing Stop Loss**: Automatically adjusts as profit increases
- **OCO Orders**: One-Cancels-Other (stop loss + take profit)
- **Bracket Orders**: Entry with automatic stop loss and take profit
- **Stop Limit Orders**: Stop trigger with limit execution price
- **Iceberg Orders**: Large orders split into smaller chunks

### 7. **Grid Trading & DCA**
- **Grid Trading**: Automated buy/sell orders at multiple price levels
- **Dollar Cost Averaging**: Systematic investment at intervals (hourly, daily, weekly)
- Strategy control (pause, resume, stop)
- Price range configuration

### 8. **User Authentication**
- JWT-based authentication
- User signup/signin pages
- Protected routes and API endpoints
- Secure token management

### 9. **Alert System**
- Multi-channel notifications (Slack, Telegram, Email)
- Trade execution alerts
- Risk threshold warnings
- Daily P&L summaries
- Error/API failure notifications

### 10. **Portfolio Analytics**
- Asset allocation charts
- P&L breakdown by trading pair
- Portfolio value tracking over time
- Win/loss streak analysis
- Tax reporting (FIFO/LIFO methods)
- Trade statistics per pair

---

## 🔧 Technical Stack

### **Backend:**
- Python 3.8+
- `aiohttp` - Async web framework
- `asyncio` - Asynchronous execution
- PostgreSQL - Database
- `gunicorn` - WSGI server (for deployment)

### **Frontend:**
- Vanilla JavaScript (no framework)
- Chart.js - Performance charts
- Lightweight Charts (TradingView-style)
- CSS3 with modern features
- Service Workers (PWA)

### **External Services:**
- Coinbase Advanced Trade API
- Claude AI (Anthropic API)
- PostgreSQL database
- Heroku (deployment target)

---

## 📊 Key Metrics Tracked

- **Total P&L**: Overall profit/loss
- **ROI**: Return on Investment percentage
- **Win Rate**: Percentage of profitable trades
- **Profit Factor**: Ratio of gross profit to gross loss
- **Sharpe Ratio**: Risk-adjusted returns
- **Maximum Drawdown**: Largest peak-to-trough decline
- **Average Win/Loss**: Trade quality metrics
- **Position Count**: Active positions
- **Daily P&L**: Daily performance tracking

---

## 🎮 Modes of Operation

### **Paper Trading Mode** (Default)
- Simulates trades without real money
- Uses real market data from Coinbase
- Realistic slippage and fees (0.6% maker/taker)
- Perfect for testing strategies safely

### **Live Trading Mode**
- Executes real trades on Coinbase
- Requires API keys with trading permissions
- All risk controls still active
- Real money at risk

---

## 🚀 Current Status

### ✅ **Completed:**
- Core trading engine with EMA+RSI+Volume strategy
- Risk management system
- REST API with all endpoints
- Web dashboard (all pages)
- User authentication system
- Backtesting engine
- AI market analysis integration
- Advanced order types
- Grid trading & DCA strategies
- Portfolio analytics
- Professional charting system
- PWA support
- Alert system
- Settings page

### 🔄 **In Progress:**
- Deployment to Heroku (configuration in progress)

### 📝 **Known Issues:**
- Heroku deployment: HEAD method route conflict (CORS/static route configuration)

---

## 🔐 Security Features

- Secure API key management
- JWT authentication
- Protected API routes
- Encrypted credentials storage
- Read-only API key option for monitoring
- Rate limit compliance
- Input validation

---

## 📁 Project Structure

```
TradingBot/
├── main.py                 # Main trading bot orchestrator
├── app.py                  # Heroku entry point
├── config.py               # Configuration management
├── requirements.txt        # Python dependencies
│
├── api/
│   └── rest_api.py        # REST API server
│
├── exchange/
│   └── coinbase_client.py # Coinbase API integration
│
├── strategy/
│   └── ema_rsi_strategy.py # Trading strategy engine
│
├── risk/
│   └── risk_manager.py    # Risk management system
│
├── orders/
│   ├── order_manager.py   # Advanced order management
│   └── order_types.py     # Order type definitions
│
├── grid_trading/
│   ├── grid_manager.py    # Grid trading engine
│   └── dca_manager.py     # DCA strategy engine
│
├── database/
│   └── db_manager.py      # PostgreSQL database manager
│
├── monitoring/
│   └── performance_tracker.py # Performance analytics
│
├── auth/
│   └── auth_manager.py    # Authentication system
│
├── alerts/
│   └── alert_manager.py   # Notification system
│
├── ai/
│   └── claude_ai.py       # Claude AI integration
│
├── backtesting/
│   ├── backtest_engine.py # Backtesting engine
│   └── historical_data.py # Historical data fetching
│
└── static/                # Frontend files
    ├── dashboard.html     # Main dashboard
    ├── dashboard.js       # Dashboard logic
    ├── styles.css         # Styling
    ├── landing.html       # Landing page
    ├── signin.html        # Sign in page
    ├── signup.html        # Sign up page
    └── ...
```

---

## 🎯 Use Cases

### **Individual Traders**
- Passive income through automated trading
- 24/7 market coverage without manual monitoring
- Systematic approach to crypto trading

### **Professional Traders**
- Scale trading operations
- Automated execution of proven strategies
- Risk-managed algorithmic trading

### **Risk-Averse Investors**
- Controlled, systematic trading
- Emotion-free decision making
- Diversification through algorithms

---

## 🚦 Running the Application

### **Local Development:**
```bash
# Install dependencies
pip install -r requirements.txt

# Setup database
createdb tradingbot

# Configure .env file
cp .env.example .env
# Edit .env with your settings

# Run the bot
python main.py
# Or start API server only
python app.py

# Access dashboard
open http://localhost:4000
```

### **Deployment:**
- Heroku (configured via Procfile)
- PostgreSQL addon required
- Environment variables configured via Heroku config

---

## 📈 Performance Targets

- **Win Rate**: >55% (target: 68.5%)
- **Profit Factor**: >1.5 (target: 1.87)
- **Sharpe Ratio**: >1.5 (target: 2.14)
- **Max Drawdown**: <5% (target: 2.3%)
- **System Uptime**: >99.9%

---

## ⚠️ Important Notes

1. **Safety First**: Always start with paper trading
2. **Risk Management**: Never trade more than you can afford to lose
3. **API Keys**: Keep credentials secure, never commit to Git
4. **Monitoring**: Regularly review performance and adjust parameters
5. **Testing**: Backtest strategies before live trading

---

## 🎓 Next Steps

1. Complete Heroku deployment configuration
2. Load testing for high-frequency scenarios
3. Additional strategy templates
4. Multi-exchange support (future enhancement)
5. Machine learning integration (future enhancement)

---

**This is a production-ready, feature-rich cryptocurrency trading bot with a professional web interface, comprehensive risk management, and AI-powered insights.**

