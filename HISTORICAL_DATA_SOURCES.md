# Historical Data Sources for Backtesting

## Overview

The backtesting system now supports **multiple data sources** with automatic fallback to ensure reliable historical data fetching.

## Data Sources

### 1. **Coinbase Exchange API** (Primary)
- **Endpoint**: `https://api.exchange.coinbase.com`
- **Format**: Public REST API
- **Rate Limit**: 300 candles per request
- **Granularity**: Supports 1m, 5m, 15m, 1h, 6h, 1d
- **Advantages**: 
  - Free, no API key required
  - Same data source as trading bot
  - Good for Coinbase-specific analysis

### 2. **Binance Public API** (Fallback)
- **Endpoint**: `https://api.binance.com`
- **Format**: Public REST API
- **Rate Limit**: 1000 candles per request (better for large datasets)
- **Granularity**: Supports 1m, 5m, 15m, 1h, 6h, 1d
- **Advantages**:
  - More reliable for historical data
  - Higher rate limits
  - Better for longer backtests
  - Automatic pair conversion (BTC-USD → BTCUSDT)

## How It Works

1. **Tries Coinbase First**: Attempts to fetch from Coinbase Exchange API
2. **Automatic Fallback**: If Coinbase returns insufficient data (< 100 candles), automatically switches to Binance
3. **Pair Conversion**: Automatically converts pair format for Binance (e.g., BTC-USD → BTCUSDT)
4. **Error Handling**: Comprehensive logging and error messages

## Pair Format Conversion

- **Coinbase**: `BTC-USD`, `ETH-USD`
- **Binance**: `BTCUSDT`, `ETHUSDT` (auto-converted)

## Usage

The backtesting system automatically uses the best available data source. No configuration needed!

## Requirements

- **Minimum**: 100 candles required for a valid backtest
- **Recommended**: 30-90 days of data for meaningful results
- **No API Keys Required**: Both sources are free public APIs

## Troubleshooting

If backtests fail with "Insufficient historical data":
1. Check internet connection
2. Verify pair format (should be BTC-USD, ETH-USD, etc.)
3. Try a shorter time period (7-14 days)
4. Check server logs for API error messages

## Future Enhancements

Potential additional data sources:
- **Polygon.io** (requires API key)
- **Alpha Vantage** (requires API key)
- **Yahoo Finance** (free, limited)
- **Local data files** (CSV import)

