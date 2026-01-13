# TradePilot User Manual

**Version 1.0** | Complete Guide to Automated Crypto Scalping

---

## Table of Contents

1. [Welcome to TradePilot](#welcome-to-tradepilot)
2. [Getting Started](#getting-started)
3. [Dashboard Overview](#dashboard-overview)
4. [Understanding the Trading Strategy](#understanding-the-trading-strategy)
5. [Pages & Features](#pages--features)
6. [Settings & Configuration](#settings--configuration)
7. [Backtesting](#backtesting)
8. [Trade Journal](#trade-journal)
9. [Learning Resources](#learning-resources)
10. [Best Practices](#best-practices)
11. [Troubleshooting](#troubleshooting)
12. [Glossary](#glossary)

---

## Welcome to TradePilot

### What is TradePilot?

TradePilot is an automated cryptocurrency scalping trading bot that helps you trade crypto with a proven EMA + RSI + Volume strategy. Unlike "black box" trading bots, TradePilot educates you on every decision it makes, helping you become a better trader while the bot executes trades.

### Key Features

- 🤖 **Automated Trading** - Trade 24/7 with minimal intervention
- 📚 **Educational** - Learn why each trade was taken with real-time explanations
- 🛡️ **Risk Management** - Built-in position sizing, stop losses, and daily limits
- 📊 **Real-Time Analysis** - See live market conditions and trade signals
- 🔬 **Backtesting** - Test strategies on historical data before going live
- 📝 **Trade Journal** - Learn from your trades with notes and pattern recognition
- 📈 **Performance Tracking** - Detailed analytics and performance metrics
- 🎓 **Learning Resources** - Glossary, strategy guide, and educational content

### Trading Strategy Overview

TradePilot uses a **confluence-based scalping strategy** that combines three technical indicators:

1. **EMA (50)** - Exponential Moving Average to identify trend direction
2. **RSI (14)** - Relative Strength Index to measure momentum
3. **Volume** - Volume confirmation to validate moves

By requiring all three indicators to align, TradePilot only takes high-quality trades with strong signals. This results in:
- High win rate (typically 55-65%+)
- Small profit targets (0.15-0.40% per trade)
- Quick exits (under 10 minutes)
- Strict risk management

---

## Getting Started

### Step 1: Create an Account

1. Visit TradePilot at your deployment URL
2. Click **"Sign Up"** on the landing page
3. Enter your email and create a password
4. Click **"Create Account"**

### Step 2: Complete Onboarding

On first login, you'll see:
1. **Welcome Modal** - Introduction to TradePilot features
2. **Risk Disclaimer** - Acknowledge trading risks (required)
3. **Guided Tour** - 6-step tour of the platform (optional)

**Tip:** Complete the guided tour to familiarize yourself with the interface. You can restart it anytime using the "🗺️ Take Tour" button in the header.

### Step 3: Configure Settings

Before trading, configure your strategy:

1. Navigate to **Settings** (⚙️ icon in sidebar)
2. Review default settings
3. Adjust parameters based on your risk tolerance:
   - **Risk Per Trade:** How much to risk per trade (default: 0.25%)
   - **Max Positions:** Maximum simultaneous trades (default: 2)
   - **Daily Loss Limit:** Auto-stop at this loss (default: $2,000)
   - **Strategy Parameters:** EMA, RSI, Volume settings
4. Select your **Trading Pairs** (default: BTC-USD, ETH-USD)
5. Click **"Save Settings"**

**Recommended for Beginners:**
- Start with **Paper Trading** enabled (default)
- Use default strategy settings initially
- Start with 1-2 trading pairs (BTC-USD, ETH-USD)
- Monitor for a few days before adjusting

### Step 4: Understand Market Conditions

Before starting the bot:

1. Navigate to **Market Conditions** page
2. Review current market analysis for each trading pair
3. Check if any trades would trigger with current conditions
4. Review AI Analysis (if Claude API key configured)

**What to Look For:**
- ✅ Green indicators = Conditions met for trading
- ⚠️ Yellow indicators = Partial conditions met
- ❌ Red indicators = Conditions not met

### Step 5: Start Trading

1. Navigate to **Overview** page
2. Review your account balance
3. Click **"▶ Start"** button in Control Panel
4. Monitor the **Bot Status** badge (should show "Running")

**Important:**
- Bot only trades when status is "Running"
- Bot checks for trades every 3-5 seconds
- Trades execute automatically when conditions are met
- You can pause or stop anytime

---

## Dashboard Overview

### Main Navigation

The left sidebar provides access to all pages:

- **Overview** - Dashboard home with bot status and quick stats
- **Market Conditions** - Real-time analysis of trading pairs
- **Positions** - Active trades (currently open)
- **Trade History** - All completed trades
- **Performance** - Analytics and metrics
- **Portfolio** - Portfolio breakdown and charts
- **Charts** - Price charts with indicators
- **Advanced Orders** - Manual order management
- **Grid Trading** - Grid trading strategies
- **Backtest** - Historical strategy testing
- **Trade Journal** - Notes, tags, and learning tools
- **Logs** - System logs and debugging
- **Glossary** - Trading terms dictionary
- **Strategy Guide** - Strategy explanation
- **Help** - FAQs and support
- **Settings** - Configuration

### Top Bar

- **Breadcrumb Navigation** - Shows current page location
- **Bot Status Badge** - Current bot status (Running/Stopped/Paused)
- **Last Update** - When data was last refreshed
- **Take Tour Button** - Restart the guided tour
- **Demo Mode Banner** - Indicates paper trading mode

### Page Refresh

- Pages auto-refresh every 5 seconds
- Manual refresh via browser refresh or page navigation
- Real-time updates for active positions

---

## Understanding the Trading Strategy

### EMA + RSI + Volume Strategy

TradePilot uses a confluence-based approach, meaning **all three indicators must align** before taking a trade. This ensures high-quality setups with strong probability.

### Long (Buy) Entry Conditions

For a LONG trade to execute, **ALL** of these must be true:

1. **Price > EMA(50)**
   - Current price must be above the 50-period Exponential Moving Average
   - Indicates an uptrend

2. **RSI Between 55-70**
   - RSI must be in the bullish range
   - Below 55 = not bullish enough
   - Above 70 = overbought (too risky)

3. **Volume > 1.5x Average**
   - Current volume must exceed 1.5x the 20-period average
   - Confirms the move has real momentum

4. **Confidence Score ≥ 70%**
   - Calculated from indicator strength
   - Ensures only high-quality setups are taken

### Short (Sell) Entry Conditions

For a SHORT trade to execute, **ALL** of these must be true:

1. **Price < EMA(50)**
   - Current price must be below the EMA
   - Indicates a downtrend

2. **RSI Between 30-45**
   - RSI must be in the bearish range
   - Above 45 = not bearish enough
   - Below 30 = oversold (too risky)

3. **Volume > 1.5x Average**
   - Volume spike confirms downward momentum

4. **Confidence Score ≥ 70%**
   - Must meet minimum confidence threshold

### Exit Strategy

Trades exit when **any** of these occur:

1. **Take Profit Hit**
   - Dynamic target: 0.15% - 0.40% profit
   - Higher confidence = higher take profit target

2. **Stop Loss Hit**
   - Dynamic limit: 0.10% - 0.50% loss
   - Protects against large losses

3. **Time Limit**
   - Maximum 10 minutes hold time
   - Exits at current price if neither TP nor SL hit
   - Keeps trades quick for scalping strategy

### Confidence Score

Confidence score (0-100%) determines trade quality:

- **Price Distance from EMA** (0-30 points)
  - Further from EMA = higher points
  - ~2%+ distance = maximum points

- **RSI Position in Range** (0-40 points)
  - Middle of range = highest points
  - Edges of range = lower points

- **Volume Confirmation** (0-30 points)
  - Higher volume = more points
  - Minimum 1.5x = 0 points, higher = more

**Example:** A trade with price 2% above EMA, RSI at 62.5 (middle), and 2x volume would score ~85%.

---

## Pages & Features

### Overview Page

**Purpose:** Your command center - see everything at a glance

**What You See:**
- **Control Panel** - Start/Pause/Resume/Stop bot controls
- **Account Balance** - Current account value
- **Total P&L** - Overall profit/loss
- **Daily P&L** - Today's profit/loss
- **ROI %** - Return on investment percentage
- **Win Rate** - Percentage of winning trades
- **Active Positions** - Number of open trades
- **Total Trades** - Lifetime trade count

**Control Buttons:**
- **▶ Start** - Start the bot (begins looking for trades)
- **⏸ Pause** - Pause new entries (manages existing positions)
- **▶ Resume** - Resume looking for new trades
- **⏹ Stop** - Stop the bot (no new trades)
- **✕ Close All** - Close all open positions immediately
- **Kill Switch** - Emergency shutdown (requires confirmation)

**When to Use:**
- Start: When you want the bot to begin trading
- Pause: When you want to stop new trades but keep existing positions open
- Stop: When you want to completely stop trading
- Close All: When you need to exit all positions quickly
- Kill Switch: Emergency situations only

### Market Conditions Page

**Purpose:** Real-time analysis of why trades are or aren't triggering

**What You See:**
For each trading pair:
- **Current Price** - Live market price
- **EMA(50)** - 50-period Exponential Moving Average
- **RSI** - Relative Strength Index (0-100)
- **Volume Ratio** - Current volume vs. average
- **Confidence Score** - Calculated trade quality (0-100%)
- **Status Indicators:**
  - ✅ Green = Condition met
  - ⚠️ Yellow = Partial condition
  - ❌ Red = Condition not met
- **Ready to Trade** - Overall status
- **AI Analysis** - AI-powered market insights (if configured)

**RSI Visual Indicators:**
- **Color-coded badges:**
  - 🔴 Overbought (>70)
  - 🟡 Long Range (55-70)
  - 🟢 Neutral (30-55)
  - 🟡 Short Range (30-45)
  - 🔴 Oversold (<30)
- **Progress bar** - Visual RSI level indicator

**How to Use:**
- Check this page to understand why no trades are happening
- Use it to verify your settings are appropriate
- Review AI Analysis for market insights
- Monitor changes in real-time

**Example Interpretation:**
- BTC-USD: Price ✅, RSI 🟡 (60), Volume ❌ (1.2x) = Not ready (volume too low)
- ETH-USD: Price ✅, RSI ✅ (65), Volume ✅ (2.1x), Confidence 85% = Ready to trade!

### Positions Page

**Purpose:** Monitor and manage active trades

**What You See:**
- **Active Positions Table:**
  - Trading pair
  - Side (LONG/SHORT)
  - Entry price
  - Current price
  - Position size
  - Current P&L ($ and %)
  - Take profit level
  - Stop loss level
  - Time held
  - Exit button (manual close)

**Position Colors:**
- 🟢 Green P&L = Profitable
- 🔴 Red P&L = Losing
- ⚪ Gray = Break-even

**How to Use:**
- Monitor open positions in real-time
- See if trades are approaching take profit or stop loss
- Manually close positions if needed (use Exit button)
- Review position details before closing

**Best Practices:**
- Let the bot manage positions automatically (recommended)
- Only manually close if you have a good reason
- Don't override stop losses - they're there for protection

### Trade History Page

**Purpose:** Review all completed trades

**What You See:**
- **Complete Trade List:**
  - Entry/Exit times
  - Trading pair
  - Side (LONG/SHORT)
  - Entry/Exit prices
  - Position size
  - P&L ($ and %)
  - Exit reason (Take Profit/Stop Loss/Timeout)
  - Tags (if added)
  - Notes (preview)
  - Edit button (to add notes/tags)

**Sorting & Filtering:**
- Trades sorted by most recent first
- Default limit: 50 most recent trades
- Can be filtered by date range (via API)

**How to Use:**
- Review past trades to understand performance
- Click "Edit" to add notes or tags for learning
- Identify patterns in winning/losing trades
- Export for record-keeping (future feature)

**Pro Tip:** Add notes to losing trades to learn from mistakes. Add tags like "good-setup" or "mistake" to track patterns.

### Performance Page

**Purpose:** Detailed analytics and performance metrics

**What You See:**

**Summary Cards:**
- **Account Balance** - Current total value
- **Total P&L** - Lifetime profit/loss
- **ROI %** - Return on investment

**Statistics:**
- **Total Trades** - Lifetime count
- **Winning Trades** - Number of profitable trades
- **Losing Trades** - Number of losing trades
- **Win Rate** - Percentage of wins
- **Profit Factor** - Gross profit / Gross loss (target: >1.5)
- **Sharpe Ratio** - Risk-adjusted return (target: >1.5)
- **Max Drawdown** - Largest peak-to-trough decline (target: <5%)
- **Average Win** - Average profit per winning trade
- **Average Loss** - Average loss per losing trade
- **Expectancy** - Expected value per trade
- **Gross Profit** - Total profits
- **Gross Loss** - Total losses

**Charts:**
- **Equity Curve** - Account balance over time
- **P&L Over Time** - Daily profit/loss chart
- **Win Rate** - Pie chart of wins vs. losses

**Performance Targets:**
Shows whether you're meeting targets:
- ✅ Win Rate >55%
- ✅ Profit Factor >1.5
- ✅ Sharpe Ratio >1.5
- ✅ Max Drawdown <5%

**How to Use:**
- Review overall performance trends
- Identify areas for improvement
- Compare actual vs. target metrics
- Use charts to visualize performance over time

### Portfolio Page

**Purpose:** Portfolio breakdown and analysis

**What You See:**
- **Portfolio Value** - Total account value
- **Total P&L** - Overall profit/loss
- **ROI** - Return on investment percentage
- **Win/Loss Streaks** - Longest winning and losing streaks

**Charts:**
- **Asset Allocation** - Trading volume by pair (pie chart)
- **P&L by Trading Pair** - Performance breakdown by pair
- **Portfolio Value Over Time** - Equity curve

**Statistics by Pair:**
- Trade count per pair
- Win rate per pair
- Total P&L per pair
- Best/worst performing pairs

**How to Use:**
- Understand which pairs perform best
- Identify diversification needs
- Track portfolio growth over time
- Analyze pair-specific performance

### Charts Page

**Purpose:** Visualize price action with indicators

**What You See:**
- **Interactive Price Chart** - TradingView-style chart
- **Trading Pair Selector** - Choose which pair to view
- **Timeframe Selector** - 1m, 5m, 15m, 1h, 4h, 1d
- **Indicator Overlays:**
  - EMA(50) line
  - Volume bars
  - Price candles

**How to Use:**
- Visualize why trades were or weren't taken
- See indicator positions relative to price
- Analyze market trends
- Understand entry/exit points

**Pro Tip:** Use this to understand why the bot took or didn't take a trade at a specific price point.

### Advanced Orders Page

**Purpose:** Manual order management (advanced users)

**What You See:**
- **Create Order Form:**
  - Order type (Market, Limit, Stop)
  - Trading pair
  - Side (BUY/SELL)
  - Size
  - Price (for limit orders)
- **Active Orders List** - Currently pending orders
- **Order History** - Past orders

**How to Use:**
- Manually place orders outside of bot strategy
- Set limit orders at specific prices
- Use stop orders for protection
- Monitor order status

**Note:** Advanced feature. Most users should let the bot trade automatically.

### Grid Trading Page

**Purpose:** Grid trading and DCA strategies (advanced)

**What You See:**
- **Grid Trading Tab:**
  - Create grid trading strategies
  - Set grid levels
  - Monitor grid performance
- **DCA (Dollar Cost Averaging) Tab:**
  - Set up DCA strategies
  - Configure intervals
  - Monitor DCA progress

**How to Use:**
- For advanced users who want additional strategies
- Grid trading: Buy/sell at multiple price levels
- DCA: Automatically invest at regular intervals

**Note:** These are advanced features separate from the main scalping strategy.

### Backtest Page

**Purpose:** Test your strategy on historical data

**What You See:**
- **Run New Backtest Form:**
  - Trading pair selector
  - Historical period (1-90+ days)
  - Initial balance
  - Backtest name
- **Quick Run Buttons:**
  - 1-Day Backtest
  - 3-Day Backtest
  - 7-Day Backtest
- **Previous Backtests:**
  - List of past backtests
  - Filter by pair and date range
  - Pagination controls

**Backtest Results Include:**
- Total P&L
- ROI percentage
- Total trades
- Win rate
- Winning/losing trades count
- Profit factor
- Sharpe ratio
- Maximum drawdown
- Equity curve
- Trade-by-trade breakdown

**How to Use:**
1. Select a trading pair
2. Choose historical period (1-7 days recommended for scalping)
3. Set initial balance (default: $100,000)
4. Give it a name (e.g., "BTC 7-Day Test")
5. Click "Run Backtest"
6. Wait for results (typically 5-30 seconds)
7. Review results and compare with live trading

**Best Practices:**
- Test before changing settings
- Use 1-7 days for scalping strategies (best accuracy)
- Compare multiple backtests
- Look for consistent performance across different periods
- Use backtest results to optimize settings

**Understanding Results:**
- **Positive P&L** = Strategy would have been profitable
- **Win Rate >55%** = Good performance
- **Profit Factor >1.5** = Profits exceed losses
- **Sharpe Ratio >1.5** = Good risk-adjusted returns
- **Max Drawdown <5%** = Acceptable risk

### Trade Journal Page

**Purpose:** Learn from your trades with notes, tags, and pattern recognition

**What You See:**
- **Tag Statistics Dashboard:**
  - Win rate by tag
  - Average P&L % by tag
  - Total P&L by tag
  - Trade count per tag

- **Search & Filters:**
  - Search notes content
  - Filter by tags
  - Filter by trading pair
  - Filter by outcome (winners/losers)

- **Trade Cards:**
  - Trade details (pair, side, prices, P&L)
  - Tags (color-coded badges)
  - Notes preview
  - Edit button

**How to Use:**

1. **Add Notes to Trades:**
   - Click "Edit" on any trade
   - Enter your thoughts in the notes field
   - Save to record lessons learned

2. **Tag Your Trades:**
   - Use common tags:
     - `good-setup` - Well-executed trades
     - `bad-setup` - Poor conditions
     - `emotions` - Emotional trading
     - `discipline` - Stuck to plan
     - `mistake` - Trading error
     - `fomo` - Fear of missing out
   - Or create custom tags
   - Multiple tags per trade allowed

3. **Identify Patterns:**
   - Review tag statistics
   - See which tags correlate with wins
   - Identify problem areas (e.g., "emotions" tag has low win rate)

4. **Learn and Improve:**
   - Regularly review journal
   - Look for patterns in losing trades
   - Adjust strategy based on insights

**Example Insights:**
- "Trades tagged 'good-setup' have 75% win rate"
- "Trades tagged 'emotions' lose an average of 0.5%"
- "I should avoid trading when feeling emotional"

### Logs Page

**Purpose:** System logs and debugging

**What You See:**
- **Log Entries:**
  - Timestamp
  - Log level (INFO, WARNING, ERROR, DEBUG)
  - Module name
  - Message
- **Filters:**
  - Filter by log level
  - Search by keyword
- **Actions:**
  - Clear view
  - Download logs (future feature)

**How to Use:**
- Debug issues
- Monitor bot activity
- Check for errors
- Understand bot behavior

**Log Levels:**
- **INFO** - Normal operations
- **WARNING** - Potential issues
- **ERROR** - Errors that need attention
- **DEBUG** - Detailed debugging information

### Glossary Page

**Purpose:** Learn trading terminology

**What You See:**
- **Searchable List** of trading terms
- **15+ Terms** including:
  - Scalping
  - EMA (Exponential Moving Average)
  - RSI (Relative Strength Index)
  - Volume
  - Take Profit
  - Stop Loss
  - Position Sizing
  - Confidence Score
  - Paper Trading
  - Backtesting
  - Risk Management
  - And more...

**Each Term Shows:**
- Definition (1-2 sentences)
- Example (practical context)
- "See it in action" link (to relevant page)

**How to Use:**
- Search for terms you don't understand
- Filter by category (Indicators, Risk, Orders, General)
- Sort alphabetically
- Click "See it in action" to see it in the app

### Strategy Guide Page

**Purpose:** Deep dive into the trading strategy

**What You See:**
- **Overview** - What is the EMA + RSI + Volume strategy
- **Entry Conditions** - Detailed LONG and SHORT requirements
- **Exit Strategy** - Take profit, stop loss, timeout explanation
- **Why It Works** - Confluence concept explanation
- **Your Current Settings** - Live display of your settings with explanations
- **Common Questions** - FAQ accordion

**How to Use:**
- Understand the strategy deeply
- See how your settings affect trading
- Learn why the strategy works
- Get answers to common questions

**Pro Tip:** Review this page after adjusting settings to ensure you understand the impact.

### Help Page

**Purpose:** FAQs and support

**What You See:**
- Frequently asked questions
- Troubleshooting tips
- Contact information
- Additional resources

**How to Use:**
- Find answers to common questions
- Troubleshoot issues
- Get support

### Settings Page

**Purpose:** Configure your trading strategy and risk management

**What You See:**

#### Strategy Parameters

- **EMA Period** (default: 50)
  - Period for Exponential Moving Average
  - Lower = more sensitive, Higher = smoother
  - Recommended: 50 (balanced)

- **RSI Period** (default: 14)
  - Period for Relative Strength Index
  - Standard: 14 (industry standard)

- **Volume Period** (default: 20)
  - Period for volume average calculation
  - Used to determine volume spikes

- **Volume Multiplier** (default: 1.5)
  - How many times average volume required
  - Higher = fewer but stronger signals
  - Lower = more signals but weaker confirmation
  - Recommended: 1.5-2.0

#### RSI Entry Thresholds

- **RSI Long Min** (default: 55)
  - Minimum RSI for LONG trades
  - Lower = more LONG opportunities

- **RSI Long Max** (default: 70)
  - Maximum RSI for LONG trades
  - Higher = allows more overbought entries

- **RSI Short Min** (default: 30)
  - Minimum RSI for SHORT trades
  - Higher = more SHORT opportunities

- **RSI Short Max** (default: 45)
  - Maximum RSI for SHORT trades
  - Lower = allows more oversold entries

#### Risk Management

- **Risk Per Trade %** (default: 0.25%)
  - Percentage of account to risk per trade
  - Lower = more conservative
  - Higher = more aggressive
  - Recommended: 0.25-0.5% for beginners

- **Max Positions** (default: 2)
  - Maximum simultaneous open trades
  - Lower = more conservative
  - Higher = more diversification
  - Recommended: 1-3 for beginners

- **Daily Loss Limit** (default: $2,000)
  - Auto-stop when daily loss reaches this amount
  - Protects account from bad days
  - Set based on account size (2-5% recommended)

- **Max Position Size %** (default: 50%)
  - Maximum % of account per position
  - Prevents over-concentration
  - Recommended: 30-50%

- **Position Timeout Minutes** (default: 10)
  - Maximum time to hold a position
  - Forces quick exits for scalping
  - Recommended: 5-10 minutes

#### Exit Parameters

- **Take Profit Min %** (default: 0.15%)
  - Minimum profit target
  - Lower = more likely to hit
  - Higher = better risk/reward

- **Take Profit Max %** (default: 0.40%)
  - Maximum profit target
  - Higher confidence = higher target
  - Range: 0.15-0.40%

- **Stop Loss Min %** (default: 0.10%)
  - Minimum stop loss distance
  - Tighter = less room for volatility
  - Looser = larger potential losses

- **Stop Loss Max %** (default: 0.50%)
  - Maximum stop loss distance
  - Higher = more room but bigger losses
  - Range: 0.10-0.50%

#### Minimum Confidence Score

- **Min Confidence Score %** (default: 70%)
  - Minimum quality required to trade
  - Higher = fewer but better trades
  - Lower = more trades but lower quality
  - Recommended: 70-85%

#### Trading Pairs

- **Selected Trading Pairs:**
  - Choose which cryptocurrencies to trade
  - Default: BTC-USD, ETH-USD
  - Can add: SOL-USD, ADA-USD, AVAX-USD, XRP-USD, DOGE-USD, MINA-USD, TRUMP-USD
  - Changes apply immediately (no restart needed)

**How to Use Settings:**

1. **For Beginners:**
   - Start with default settings
   - Monitor performance for a few days
   - Only adjust if needed

2. **For More Trades:**
   - Lower Volume Multiplier (1.3-1.5)
   - Lower Min Confidence (65-70%)
   - Widen RSI ranges (Long: 50-75, Short: 25-50)
   - Increase Max Positions (3-5)

3. **For Better Quality:**
   - Higher Volume Multiplier (1.8-2.0)
   - Higher Min Confidence (75-85%)
   - Narrow RSI ranges (Long: 60-70, Short: 30-40)
   - Lower Max Positions (1-2)

4. **Always:**
   - Test changes with backtesting first
   - Make small adjustments (one at a time)
   - Monitor results before further changes
   - Save settings after changes

**Settings Tips:**
- ⚠️ **Never risk more than you can afford to lose**
- 📊 **Use backtesting before changing settings**
- 🔄 **Changes to trading pairs apply immediately**
- 💾 **Always click "Save Settings" after changes**
- 🔄 **Use "Apply & Restart" if bot doesn't respond**

---

## Settings & Configuration

### Understanding Your Settings

#### Conservative Settings (Fewer Trades, Higher Quality)
- Volume Multiplier: 2.0
- Min Confidence: 80%
- RSI Long: 60-70
- RSI Short: 30-40
- Max Positions: 1
- **Expected:** 2-5 trades per day

#### Balanced Settings (Recommended)
- Volume Multiplier: 1.5
- Min Confidence: 70%
- RSI Long: 55-70
- RSI Short: 30-45
- Max Positions: 2
- **Expected:** 5-15 trades per day

#### Aggressive Settings (More Trades, Lower Quality)
- Volume Multiplier: 1.3
- Min Confidence: 65%
- RSI Long: 50-75
- RSI Short: 25-50
- Max Positions: 3
- **Expected:** 15-30+ trades per day

### Changing Settings

1. Navigate to **Settings** page
2. Modify desired parameters
3. Review help tooltips (ℹ️ icons)
4. Click **"Save Settings"**
5. Changes apply immediately (trading pairs) or require restart (strategy params)

**Important:** Changes to trading pairs apply immediately without restart. Changes to strategy parameters may require a restart to take full effect.

---

## Backtesting

### What is Backtesting?

Backtesting allows you to test your strategy on historical data to see how it would have performed. This helps you:
- Validate strategy effectiveness
- Optimize settings before going live
- Understand expected performance
- Build confidence in the strategy

### How to Run a Backtest

1. Navigate to **Backtest** page
2. Choose a **Trading Pair** (e.g., BTC-USD)
3. Select **Historical Period:**
   - 1 day - Quick test, most accurate
   - 3 days - Short-term performance
   - 7 days - Weekly performance (recommended)
   - 14+ days - Longer-term trends (uses optimized granularity)

4. Set **Initial Balance** (default: $100,000)
5. Enter a **Backtest Name** (e.g., "BTC 7-Day Test Dec 2025")
6. Click **"Run Backtest"** or use quick-run buttons

### Understanding Backtest Results

**Key Metrics:**

- **Total P&L** - Total profit/loss
- **ROI %** - Return on investment percentage
- **Total Trades** - Number of trades executed
- **Win Rate** - Percentage of winning trades
- **Profit Factor** - Gross profit / Gross loss
- **Sharpe Ratio** - Risk-adjusted return
- **Max Drawdown** - Largest decline from peak

**What Good Results Look Like:**
- ✅ Win Rate >55%
- ✅ Profit Factor >1.5
- ✅ Sharpe Ratio >1.5
- ✅ Max Drawdown <5%
- ✅ Consistent positive P&L

**What to Watch For:**
- ⚠️ High win rate but negative P&L = Stop losses too tight
- ⚠️ Low win rate = Strategy may not suit market conditions
- ⚠️ High drawdown = Too much risk per trade
- ⚠️ Very few trades = Settings too strict

### Backtest Best Practices

1. **Test Multiple Periods:**
   - Test 1, 3, and 7 days
   - Compare consistency
   - Look for patterns

2. **Test Different Settings:**
   - Run backtests with different parameters
   - Compare results
   - Find optimal settings

3. **Test Multiple Pairs:**
   - Some pairs perform better than others
   - Find pairs that suit your strategy
   - Diversify across pairs

4. **Review Trade Details:**
   - Look at individual trades
   - Understand entry/exit points
   - Identify improvement opportunities

5. **Compare with Live Trading:**
   - Backtest results are estimates
   - Real trading includes slippage and fees
   - Use backtests as guidance, not guarantees

---

## Trade Journal

### Why Keep a Trade Journal?

A trade journal helps you:
- Learn from wins and losses
- Identify patterns in your trading
- Improve decision-making
- Track emotional state
- Build trading discipline

### How to Use the Trade Journal

#### Adding Notes to Trades

1. Navigate to **Trade History** or **Trade Journal**
2. Click **"Edit"** on any trade
3. Enter your thoughts in the notes field:
   - What did you learn?
   - What would you do differently?
   - What market conditions were present?
   - How did you feel?
4. Click **"Save"**

#### Tagging Trades

1. Click **"Edit"** on a trade
2. Add tags:
   - Select from common tags dropdown
   - Or type a custom tag
   - Press Enter or click "Add"
3. Remove tags by clicking the × button
4. Click **"Save"**

**Common Tags:**
- `good-setup` - Strong entry conditions
- `bad-setup` - Weak entry conditions
- `emotions` - Emotional decision
- `discipline` - Followed plan
- `mistake` - Trading error
- `fomo` - Fear of missing out
- `revenge` - Revenge trading
- `patience` - Waited for setup
- `followed-plan` - Stuck to strategy
- `deviated-plan` - Changed strategy mid-trade

#### Understanding Pattern Recognition

The journal automatically calculates statistics for each tag:

- **Win Rate by Tag** - Which tags correlate with wins?
- **Avg P&L % by Tag** - Which tags are most profitable?
- **Total P&L by Tag** - Overall performance per tag
- **Trade Count** - How many trades per tag

**Example Insights:**
- "Trades tagged 'good-setup' have 75% win rate" = Focus on these setups
- "Trades tagged 'emotions' have 40% win rate" = Avoid emotional trading
- "Trades tagged 'discipline' are more profitable" = Follow your plan

#### Using Filters

Use filters to analyze specific trades:
- **Search** - Find trades with specific notes
- **Tag Filter** - See all trades with a specific tag
- **Pair Filter** - Analyze specific trading pairs
- **Outcome Filter** - Compare winners vs. losers

---

## Learning Resources

### Glossary

The **Glossary** page contains definitions of all trading terms used in TradePilot. Each term includes:
- Clear definition
- Practical example
- Link to see it in action

**Access:** Click "📚 Glossary" in the sidebar navigation

### Strategy Guide

The **Strategy Guide** explains:
- How the EMA + RSI + Volume strategy works
- Entry conditions in detail
- Exit strategy explanation
- Why the strategy works (confluence)
- Your current settings with explanations
- Common questions

**Access:** Click "📖 Strategy Guide" in the sidebar navigation

### Guided Tour

The **Guided Tour** walks you through:
1. Dashboard overview
2. Market Conditions analysis
3. Bot controls
4. Charts visualization
5. Settings configuration
6. Backtesting features

**Access:** Click "🗺️ Take Tour" button in the header (anytime)

### Help & FAQs

The **Help** page provides:
- Frequently asked questions
- Troubleshooting tips
- Contact information
- Additional resources

**Access:** Click "Help" in the sidebar navigation

---

## Best Practices

### For Beginners

1. **Start with Paper Trading**
   - Practice with virtual money first
   - Learn how the bot works
   - Build confidence before going live

2. **Use Default Settings Initially**
   - Default settings are tested and balanced
   - Monitor for a few days
   - Only adjust when you understand the impact

3. **Start with Few Trading Pairs**
   - Begin with BTC-USD and ETH-USD
   - Add more pairs gradually
   - Focus on quality over quantity

4. **Monitor Regularly**
   - Check Market Conditions page daily
   - Review trade history weekly
   - Analyze performance monthly

5. **Keep a Trade Journal**
   - Add notes to every trade
   - Tag trades for pattern recognition
   - Learn from both wins and losses

6. **Test Before Changing**
   - Always backtest before changing settings
   - Make small adjustments
   - Monitor results

### Risk Management

1. **Never Risk More Than You Can Afford**
   - Only trade with disposable income
   - Set appropriate daily loss limits
   - Don't chase losses

2. **Use Conservative Risk Settings**
   - Start with 0.25% risk per trade
   - Set daily loss limit at 2-5% of account
   - Limit max positions to 1-2

3. **Respect Stop Losses**
   - Never disable stop losses
   - Don't manually override stops
   - Trust the risk management system

4. **Diversify Carefully**
   - Don't over-diversify (spread too thin)
   - Focus on 2-5 quality pairs
   - Monitor correlation between pairs

### Strategy Optimization

1. **Backtest Before Changes**
   - Test all setting changes
   - Compare multiple backtests
   - Look for consistency

2. **Make Incremental Changes**
   - Change one parameter at a time
   - Monitor results for each change
   - Document what works

3. **Focus on Quality Over Quantity**
   - Better to have fewer high-quality trades
   - Don't sacrifice quality for frequency
   - Let the confidence score guide you

4. **Review Performance Regularly**
   - Weekly performance reviews
   - Monthly strategy analysis
   - Quarterly optimization

### Emotional Trading

1. **Trust the Bot**
   - Let the bot execute trades automatically
   - Don't interfere with running positions
   - Review decisions after trades close

2. **Avoid Revenge Trading**
   - Don't increase risk after losses
   - Stick to your plan
   - Take breaks if emotional

3. **Use the Trade Journal**
   - Tag emotional trades
   - Review emotional patterns
   - Build discipline over time

4. **Set It and Forget It**
   - Configure settings thoughtfully
   - Start the bot
   - Check periodically, not constantly

---

## Troubleshooting

### Bot Not Trading

**Problem:** Bot status is "Running" but no trades are executing.

**Possible Causes:**
1. **Market conditions don't meet criteria**
   - Check Market Conditions page
   - Verify all indicators are green
   - Review confidence scores

2. **Settings too strict**
   - Volume multiplier too high
   - Confidence threshold too high
   - RSI ranges too narrow

3. **Max positions reached**
   - Check Positions page
   - Close existing positions if needed
   - Reduce Max Positions setting

4. **Daily loss limit reached**
   - Check performance metrics
   - Reset daily limit if needed
   - Wait until next day (auto-reset)

**Solutions:**
- Review Market Conditions page to see what's missing
- Check bot logs for errors
- Verify settings are appropriate
- Test with backtesting to confirm settings work

### Trades Closing Immediately

**Problem:** Trades open but close right away.

**Possible Causes:**
1. **Take profit hit immediately**
   - Very tight profit targets
   - High volatility market
   - Slippage causing immediate TP

2. **Stop loss hit immediately**
   - Too tight stop loss
   - Market gap
   - Slippage

**Solutions:**
- Review trade details in Trade History
- Check exit reason (should show TP or SL)
- Adjust take profit/stop loss ranges if needed
- Consider wider ranges for volatile pairs

### High Loss Rate

**Problem:** More losing trades than winning trades.

**Possible Causes:**
1. **Settings too aggressive**
   - Confidence threshold too low
   - Volume multiplier too low
   - RSI ranges too wide

2. **Market conditions**
   - Choppy/consolidating market
   - Low volatility
   - Trend changes

3. **Stop losses too tight**
   - Getting stopped out before TP
   - Need wider stop loss range

**Solutions:**
- Review losing trades in journal
- Look for patterns (tag trades)
- Adjust settings to be more conservative
- Use backtesting to test changes
- Consider pausing during choppy markets

### No Trades for Days

**Problem:** Bot running but no trades for several days.

**Possible Causes:**
1. **Settings very conservative**
   - High confidence threshold
   - High volume multiplier
   - Narrow RSI ranges

2. **Market conditions**
   - Sideways market
   - Low volatility
   - Unfavorable trends

3. **Trading pairs**
   - Limited pairs selected
   - Pairs not meeting conditions

**Solutions:**
- Check Market Conditions page
- Review if any pairs are close to meeting conditions
- Consider adding more trading pairs
- Slightly relax settings (test with backtesting first)
- This may be normal - quality over quantity

### Error Messages

**Common Errors:**

1. **"Bot not initialized"**
   - Bot service not running
   - Restart the bot service
   - Check deployment logs

2. **"Database not initialized"**
   - Database connection issue
   - Check database credentials
   - Verify database is running

3. **"Authentication required"**
   - Session expired
   - Log out and log back in
   - Clear browser cache

4. **"API timeout"**
   - Request took too long
   - Try again
   - Check network connection

**Solutions:**
- Check Logs page for detailed errors
- Review browser console (F12)
- Contact support if issue persists

### Performance Issues

**Problem:** Pages loading slowly or not responding.

**Solutions:**
- Clear browser cache
- Refresh the page
- Check internet connection
- Try different browser
- Disable browser extensions

---

## Glossary

### Core Trading Terms

**Scalping** - Trading strategy that profits from small price changes by making many trades throughout the day. Scalpers target 0.1-0.5% profit per trade.

**EMA (Exponential Moving Average)** - A type of moving average that gives more weight to recent prices, making it more responsive to new information than Simple Moving Average. TradePilot uses EMA(50) to identify trend direction.

**RSI (Relative Strength Index)** - A momentum indicator measuring the speed and magnitude of price changes on a scale of 0-100. Values above 70 suggest overbought; below 30 suggest oversold.

**Volume** - The number of shares or contracts traded in a security or market during a given period. High volume confirms the strength of price movements.

**Confidence Score** - A 0-100% score indicating the strength of a trading signal. Higher scores mean stronger alignment of indicators (EMA, RSI, Volume).

### Risk Management Terms

**Take Profit** - A predetermined price level at which a trader closes a profitable position to lock in gains. TradePilot uses dynamic take profit based on confidence score (0.15-0.40%).

**Stop Loss** - A predetermined price level at which a trader closes a losing position to limit losses. TradePilot uses dynamic stop loss (0.10-0.50%).

**Position Sizing** - The amount of capital allocated to a single trade. TradePilot calculates position size based on risk per trade percentage and stop loss distance.

**Daily Loss Limit** - Maximum acceptable loss per day. When reached, bot automatically stops trading to protect the account.

**Max Positions** - Maximum number of simultaneous open trades. Prevents over-concentration and manages risk.

### Trading Terms

**Trading Pair** - Two assets traded against each other. TradePilot trades cryptocurrency pairs like BTC-USD (Bitcoin vs US Dollar).

**LONG** - A buy position. Profit when price goes up.

**SHORT** - A sell position. Profit when price goes down.

**Entry Price** - Price at which a trade is opened.

**Exit Price** - Price at which a trade is closed.

**P&L (Profit & Loss)** - The profit or loss on a trade, calculated as (Exit Price - Entry Price) × Position Size.

**ROI (Return on Investment)** - Percentage return on invested capital, calculated as (Current Balance - Initial Balance) / Initial Balance × 100.

**Win Rate** - Percentage of trades that are profitable, calculated as Winning Trades / Total Trades × 100.

### Strategy Terms

**Confluence** - The concept that multiple independent indicators confirming the same signal significantly increases the probability of success.

**Entry Signal** - When all entry conditions are met and a trade is initiated.

**Exit Signal** - When an exit condition (take profit, stop loss, or timeout) is met and a trade is closed.

**Market Conditions** - Current state of market indicators (price, EMA, RSI, volume) that determine if trades can be taken.

### Platform Terms

**Paper Trading** - Simulated trading using real market data but fake money. Allows testing strategies risk-free.

**Backtesting** - Testing a trading strategy on historical data to see how it would have performed.

**Live Trading** - Real trading with actual money and real executions.

**Demo Mode** - Indicates paper trading mode (no real money at risk).

---

## Frequently Asked Questions

### General Questions

**Q: How much money do I need to start?**
A: TradePilot works with any account size. For paper trading, you start with $100,000 virtual money. For live trading, start with an amount you can afford to lose. Many users start with $1,000-$10,000.

**Q: Can I use TradePilot on mobile?**
A: Yes! TradePilot is mobile-responsive. You can access it from any device with a web browser. However, a larger screen (desktop/tablet) provides the best experience.

**Q: Do I need to monitor TradePilot 24/7?**
A: No! TradePilot runs automatically. You should check periodically (daily is recommended) but don't need to watch constantly. The bot will execute trades and manage positions automatically.

**Q: What cryptocurrencies can I trade?**
A: TradePilot supports any trading pair available on Coinbase. Default pairs are BTC-USD and ETH-USD. You can add: SOL, ADA, AVAX, XRP, DOGE, MINA, TRUMP, and more.

### Strategy Questions

**Q: Why aren't I seeing any trades?**
A: This usually means market conditions don't meet your strategy's strict criteria. Check the Market Conditions page to see what's missing. Your settings may also be too conservative. Try relaxing Volume Multiplier or Confidence Score slightly (after backtesting).

**Q: How many trades should I expect per day?**
A: This depends on your settings and market conditions. With balanced settings: 5-15 trades per day. With conservative settings: 2-5 trades. With aggressive settings: 15-30+ trades. Remember: quality over quantity!

**Q: Can I modify the trading strategy?**
A: Yes! You can adjust all parameters in Settings:
- EMA period
- RSI ranges
- Volume multiplier
- Confidence threshold
- Exit parameters

**Q: What's a good win rate?**
A: A win rate above 55% is considered good for scalping. TradePilot typically achieves 55-65% win rates with balanced settings. However, win rate alone doesn't tell the full story - profit factor and risk/reward matter too.

**Q: Why do some trades timeout?**
A: Trades timeout after 10 minutes (default) if neither take profit nor stop loss is hit. This keeps trades quick for scalping. The trade closes at the current market price.

### Risk Management Questions

**Q: What's a safe risk per trade?**
A: For beginners, 0.25% risk per trade is recommended. This means if you have $10,000, you risk $25 per trade. More experienced traders may use 0.5-1%, but never risk more than you can afford to lose.

**Q: Should I set a daily loss limit?**
A: Yes! Daily loss limits protect your account from bad days. Recommended: 2-5% of account size. For a $10,000 account, set limit to $200-$500.

**Q: What happens if I hit my daily loss limit?**
A: The bot automatically stops trading and closes all open positions. Trading resumes the next day when the limit resets. This prevents catastrophic losses.

**Q: Can I disable stop losses?**
A: No, and you shouldn't! Stop losses are essential for risk management. They protect you from large losses. Never disable or override them.

### Technical Questions

**Q: What's the difference between Paper Trading and Live Trading?**
A: Paper Trading uses virtual money with real market data. No real money is at risk. Live Trading uses real money and executes real trades. Always start with Paper Trading!

**Q: How do I switch from Paper Trading to Live Trading?**
A: In Settings, set `PAPER_TRADING=false` (requires environment variable change on server). However, we strongly recommend extensive paper trading practice first.

**Q: Do I need Coinbase API keys?**
A: For paper trading with real market data, API keys are optional. For live trading, you need Coinbase Advanced Trade API credentials.

**Q: What happens if my internet disconnects?**
A: The bot runs on the server, so brief internet disconnections won't affect it. However, if the server goes down, trading stops until it's back online.

### Performance Questions

**Q: What's a good profit factor?**
A: Profit factor above 1.5 is considered good. This means profits are at least 1.5x larger than losses. TradePilot targets 1.5+ with balanced settings.

**Q: What's a good Sharpe ratio?**
A: Sharpe ratio above 1.5 indicates good risk-adjusted returns. This means returns are high relative to volatility/risk taken.

**Q: What's maximum drawdown?**
A: Maximum drawdown is the largest peak-to-trough decline in account value. Lower is better. TradePilot targets <5% maximum drawdown.

**Q: How long should I test before going live?**
A: We recommend at least 30 days of paper trading with consistent positive results before considering live trading. This gives you enough data to assess performance.

### Backtesting Questions

**Q: How long should I backtest?**
A: For scalping, 1-7 days is most accurate. Longer periods (14-90 days) use optimized granularity but may be less precise for minute-level scalping.

**Q: Why don't backtest results match live trading?**
A: Backtests use historical data and don't account for:
- Slippage (price difference between expected and actual execution)
- Fees
- Market impact
- Real-time execution delays

Backtests are estimates, not guarantees.

**Q: How often should I backtest?**
A: Backtest before making any setting changes. Also backtest monthly to ensure strategy still works. Market conditions change, so regular testing is important.

### Journal Questions

**Q: Why should I keep a trade journal?**
A: A trade journal helps you learn from your trades, identify patterns, and improve over time. It's one of the most valuable tools for becoming a better trader.

**Q: What tags should I use?**
A: Use tags that help you identify patterns:
- `good-setup` / `bad-setup` - Trade quality
- `emotions` / `discipline` - Emotional state
- `mistake` - Errors to learn from
- `followed-plan` / `deviated-plan` - Adherence to plan

**Q: How often should I review my journal?**
A: Review weekly to identify patterns. Monthly deep dives help with strategy optimization. Regular review is key to improvement.

---

## Getting Help

### Resources

1. **Glossary** - Look up any trading term
2. **Strategy Guide** - Deep dive into the strategy
3. **Help Page** - FAQs and troubleshooting
4. **Guided Tour** - Walkthrough of the platform
5. **Trade Journal** - Learn from your trades

### Support

- Check the **Logs** page for error messages
- Review **Market Conditions** to understand why trades aren't happening
- Use **Backtesting** to test changes before applying
- Review this manual for common issues

---

## Appendix

### Default Settings Reference

```
Strategy Parameters:
- EMA Period: 50
- RSI Period: 14
- Volume Period: 20
- Volume Multiplier: 1.5x
- RSI Long Range: 55-70
- RSI Short Range: 30-45
- Min Confidence Score: 70%

Risk Management:
- Risk Per Trade: 0.25%
- Max Positions: 2
- Daily Loss Limit: $2,000
- Max Position Size: 50%
- Position Timeout: 10 minutes

Exit Parameters:
- Take Profit Range: 0.15-0.40%
- Stop Loss Range: 0.10-0.50%

Trading Pairs:
- Default: BTC-USD, ETH-USD
- Available: SOL-USD, ADA-USD, AVAX-USD, XRP-USD, DOGE-USD, MINA-USD, TRUMP-USD
```

### Keyboard Shortcuts

- `Ctrl/Cmd + R` - Refresh page
- `F12` - Open browser developer console
- `Esc` - Close modals

### Performance Targets

TradePilot aims for:
- ✅ Win Rate: >55%
- ✅ Profit Factor: >1.5
- ✅ Sharpe Ratio: >1.5
- ✅ Max Drawdown: <5%

### Trading Hours

Cryptocurrency markets trade 24/7. TradePilot can trade at any time. However:
- Highest volume: US market hours (9 AM - 4 PM EST)
- Best opportunities: During high volatility periods
- Lowest activity: Weekends and holidays (still trades, just fewer opportunities)

---

## Conclusion

TradePilot is designed to be more than just a trading bot - it's a learning platform that helps you become a better trader while the bot handles execution. Use the educational features, keep a journal, and continuously improve your understanding of the markets.

Remember:
- ✅ Start with paper trading
- ✅ Use default settings initially
- ✅ Monitor and learn
- ✅ Keep a trade journal
- ✅ Never risk more than you can afford to lose
- ✅ Trust the risk management system

**Happy Trading!**

---

**TradePilot User Manual v1.0**  
*Last Updated: After Phase 2A Implementation*  
*For questions or support, refer to the Help page*

