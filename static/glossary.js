/**
 * Glossary Data and Functions
 */

const glossaryTerms = [
    {
        term: "Scalping",
        definition: "A trading strategy that profits from small price changes by making many trades throughout the day. Scalpers target small profits (typically 0.1-0.5%) per trade.",
        example: "A scalper might make 20 trades per day, each targeting 0.2-0.5% profit. They hold positions for minutes, not hours.",
        category: "general",
        seeItInAction: "/market-conditions"
    },
    {
        term: "EMA (Exponential Moving Average)",
        definition: "A type of moving average that gives more weight to recent prices, making it more responsive to new information than Simple Moving Average (SMA).",
        example: "When price crosses above the 50 EMA, it often signals bullish momentum. TradePilot uses EMA(50) to identify trend direction.",
        category: "indicators",
        seeItInAction: "/charts"
    },
    {
        term: "RSI (Relative Strength Index)",
        definition: "A momentum indicator measuring the speed and magnitude of price changes on a scale of 0-100. Values above 70 suggest overbought conditions; below 30 suggest oversold.",
        example: "RSI above 70 suggests the asset may be overbought and due for a pullback. RSI below 30 suggests it may be oversold and due for a bounce.",
        category: "indicators",
        seeItInAction: "/market-conditions"
    },
    {
        term: "Volume",
        definition: "The number of shares or contracts traded in a security or market during a given period. High volume confirms the strength of price movements.",
        example: "If price rises on high volume, it confirms the uptrend. If price rises on low volume, it may be a false breakout.",
        category: "indicators",
        seeItInAction: "/market-conditions"
    },
    {
        term: "Take Profit",
        definition: "A predetermined price level at which a trader closes a profitable position to lock in gains. TradePilot uses dynamic take profit based on confidence score.",
        example: "If you enter a LONG at $100 and set take profit at $100.30 (0.3% profit), the position automatically closes when price reaches $100.30.",
        category: "orders",
        seeItInAction: "/positions"
    },
    {
        term: "Stop Loss",
        definition: "A predetermined price level at which a trader closes a losing position to limit losses. Essential for risk management.",
        example: "If you enter a LONG at $100 and set stop loss at $99.80 (0.2% loss), the position automatically closes if price drops to $99.80.",
        category: "risk",
        seeItInAction: "/positions"
    },
    {
        term: "Position Sizing",
        definition: "The amount of capital allocated to a single trade. TradePilot calculates position size based on your risk per trade percentage and stop loss distance.",
        example: "With $100,000 account and 0.25% risk per trade, you risk $250 per trade. Position size is calculated to ensure losses don't exceed this amount.",
        category: "risk",
        seeItInAction: "/settings"
    },
    {
        term: "Confidence Score",
        definition: "A 0-100% score indicating the strength of a trading signal. Higher scores mean stronger alignment of indicators (EMA, RSI, Volume).",
        example: "A 85% confidence score means all indicators are strongly aligned. A 70% score is the minimum required to take a trade.",
        category: "indicators",
        seeItInAction: "/market-conditions"
    },
    {
        term: "Paper Trading",
        definition: "Simulated trading using real market data but fake money. Allows you to test strategies risk-free before using real capital.",
        example: "Paper trading lets you practice with $100,000 virtual money. You see real market prices but no actual trades are executed.",
        category: "general",
        seeItInAction: "/settings"
    },
    {
        term: "Backtesting",
        definition: "Testing a trading strategy on historical data to see how it would have performed. Helps validate strategies before live trading.",
        example: "Running a 7-day backtest shows how your strategy would have performed over the last week using historical price data.",
        category: "general",
        seeItInAction: "/backtest"
    },
    {
        term: "Risk Management",
        definition: "The practice of identifying, assessing, and controlling risks in trading. Includes position sizing, stop losses, and daily loss limits.",
        example: "Good risk management means never risking more than 1-2% of your account on a single trade and having daily loss limits.",
        category: "risk",
        seeItInAction: "/settings"
    },
    {
        term: "Leverage",
        definition: "Borrowed capital used to increase potential returns. TradePilot does not use leverage, trading only with available capital.",
        example: "With 10x leverage, a $1,000 trade controls $10,000. This amplifies both profits and losses. TradePilot avoids this risk.",
        category: "risk",
        seeItInAction: "/settings"
    },
    {
        term: "Slippage",
        definition: "The difference between expected execution price and actual execution price. Common during high volatility or low liquidity.",
        example: "You expect to buy at $100 but actual execution is $100.05 due to slippage. TradePilot simulates realistic slippage in paper trading.",
        category: "orders",
        seeItInAction: "/trades"
    },
    {
        term: "Trading Pair",
        definition: "Two assets traded against each other. TradePilot trades cryptocurrency pairs like BTC-USD (Bitcoin vs US Dollar).",
        example: "BTC-USD means trading Bitcoin priced in US Dollars. ETH-USD means trading Ethereum priced in US Dollars.",
        category: "general",
        seeItInAction: "/market-conditions"
    },
    {
        term: "Market Order",
        definition: "An order to buy or sell immediately at the current market price. TradePilot uses market orders for quick execution.",
        example: "Placing a market order to buy BTC-USD immediately executes at whatever the current market price is (e.g., $97,500).",
        category: "orders",
        seeItInAction: "/orders"
    }
];

let glossarySortedAlphabetically = false;

function populateGlossary() {
    const container = document.getElementById('glossaryTerms');
    if (!container) return;

    const searchTerm = document.getElementById('glossarySearch')?.value.toLowerCase() || '';
    const category = document.getElementById('glossaryCategory')?.value || 'all';

    let filtered = glossaryTerms.filter(term => {
        const matchesSearch = term.term.toLowerCase().includes(searchTerm) || 
                             term.definition.toLowerCase().includes(searchTerm);
        const matchesCategory = category === 'all' || term.category === category;
        return matchesSearch && matchesCategory;
    });

    if (glossarySortedAlphabetically) {
        filtered.sort((a, b) => a.term.localeCompare(b.term));
    }

    if (filtered.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: var(--gray-500); padding: 2rem;">No terms found matching your search.</p>';
        return;
    }

    container.innerHTML = filtered.map(term => `
        <div class="glossary-card">
            <div class="glossary-card-header">
                <h3>${escapeHtml(term.term)}</h3>
                <span class="glossary-category-badge category-${term.category}">${term.category}</span>
            </div>
            <div class="glossary-card-body">
                <p class="glossary-definition">${escapeHtml(term.definition)}</p>
                <div class="glossary-example">
                    <strong>Example:</strong> ${escapeHtml(term.example)}
                </div>
                <a href="${term.seeItInAction}" class="glossary-action-link" onclick="event.preventDefault(); navigateToPage('${term.seeItInAction.replace('/', '')}');">
                    See it in action →
                </a>
            </div>
        </div>
    `).join('');
}

function sortGlossaryAlphabetically() {
    glossarySortedAlphabetically = !glossarySortedAlphabetically;
    populateGlossary();
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Initialize glossary when page loads
document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('glossarySearch');
    const categorySelect = document.getElementById('glossaryCategory');
    
    if (searchInput) {
        searchInput.addEventListener('input', populateGlossary);
    }
    
    if (categorySelect) {
        categorySelect.addEventListener('change', populateGlossary);
    }
    
    // Initial population
    if (document.getElementById('glossaryTerms')) {
        populateGlossary();
    }
});

