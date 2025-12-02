"""Historical data fetcher for backtesting with multiple data sources."""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import aiohttp
from config import get_config

logger = logging.getLogger(__name__)


class HistoricalDataFetcher:
    """Fetches historical market data for backtesting from multiple sources."""
    
    def __init__(self, config=None):
        self.config = config or get_config()
        self.coinbase_url = "https://api.exchange.coinbase.com"
        self.binance_url = "https://api.binance.com"
        logger.info("HistoricalDataFetcher initialized with multiple data sources")
    
    async def fetch_candles(
        self, 
        pair: str, 
        start_date: datetime, 
        end_date: datetime, 
        granularity: str = 'ONE_MINUTE'
    ) -> List[Dict]:
        """
        Fetch historical candles from multiple sources (tries Coinbase first, then Binance).
        
        Args:
            pair: Trading pair (e.g., 'BTC-USD')
            start_date: Start datetime
            end_date: End datetime
            granularity: Candle granularity (ONE_MINUTE, FIVE_MINUTE, etc.)
        
        Returns:
            List of candle dictionaries
        """
        # Try Coinbase first
        candles = await self._fetch_from_coinbase(pair, start_date, end_date, granularity)
        
        # If Coinbase fails, try Binance as fallback
        if not candles or len(candles) < 100:
            logger.warning(f"Coinbase returned {len(candles) if candles else 0} candles, trying Binance...")
            candles = await self._fetch_from_binance(pair, start_date, end_date, granularity)
        
        if candles and len(candles) >= 100:
            logger.info(f"Successfully fetched {len(candles)} candles for {pair} from {start_date} to {end_date}")
        else:
            logger.error(f"Failed to fetch sufficient candles. Got {len(candles) if candles else 0} candles, need at least 100")
        
        return candles or []
    
    async def _fetch_from_coinbase(
        self,
        pair: str,
        start_date: datetime,
        end_date: datetime,
        granularity: str
    ) -> List[Dict]:
        """Fetch candles from Coinbase Exchange API."""
        try:
            candles = []
            current_start = start_date
            
            # Coinbase API limits to 300 candles per request
            max_candles_per_request = 300
            
            # Granularity to seconds mapping
            granularity_seconds = {
                'ONE_MINUTE': 60,
                'FIVE_MINUTE': 300,
                'FIFTEEN_MINUTE': 900,
                'ONE_HOUR': 3600,
                'SIX_HOUR': 21600,
                'ONE_DAY': 86400
            }
            
            interval_seconds = granularity_seconds.get(granularity, 60)
            granularity_num = interval_seconds
            
            async with aiohttp.ClientSession() as session:
                while current_start < end_date:
                    batch_end = current_start + timedelta(
                        seconds=interval_seconds * max_candles_per_request
                    )
                    if batch_end > end_date:
                        batch_end = end_date
                    
                    batch_candles = await self._fetch_batch_coinbase(
                        session, pair, current_start, batch_end, granularity_num
                    )
                    
                    if not batch_candles:
                        break
                    
                    candles.extend(batch_candles)
                    current_start = batch_end
                    await asyncio.sleep(0.5)
            
            return candles
            
        except Exception as e:
            logger.error(f"Failed to fetch from Coinbase: {e}", exc_info=True)
            return []
    
    async def _fetch_from_binance(
        self,
        pair: str,
        start_date: datetime,
        end_date: datetime,
        granularity: str
    ) -> List[Dict]:
        """Fetch candles from Binance public API (more reliable for historical data)."""
        try:
            # Convert pair format: BTC-USD -> BTCUSDT
            binance_pair = pair.replace('-', '').replace('USD', 'USDT')
            
            # Binance interval mapping
            binance_intervals = {
                'ONE_MINUTE': '1m',
                'FIVE_MINUTE': '5m',
                'FIFTEEN_MINUTE': '15m',
                'ONE_HOUR': '1h',
                'SIX_HOUR': '6h',
                'ONE_DAY': '1d'
            }
            
            interval = binance_intervals.get(granularity, '1m')
            
            candles = []
            start_time = int(start_date.timestamp() * 1000)  # Binance uses milliseconds
            end_time = int(end_date.timestamp() * 1000)
            
            async with aiohttp.ClientSession() as session:
                url = f"{self.binance_url}/api/v3/klines"
                
                while start_time < end_time:
                    params = {
                        'symbol': binance_pair,
                        'interval': interval,
                        'startTime': start_time,
                        'endTime': end_time,
                        'limit': 1000  # Binance allows up to 1000 candles per request
                    }
                    
                    async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=30)) as response:
                        if response.status == 200:
                            data = await response.json()
                            
                            if not isinstance(data, list):
                                break
                            
                            for candle in data:
                                if len(candle) >= 6:
                                    candles.append({
                                        'timestamp': datetime.fromtimestamp(candle[0] / 1000),
                                        'open': float(candle[1]),
                                        'high': float(candle[2]),
                                        'low': float(candle[3]),
                                        'close': float(candle[4]),
                                        'volume': float(candle[5])
                                    })
                            
                            # Update start_time for next batch
                            if data:
                                start_time = int(data[-1][0]) + 1  # Last candle timestamp + 1ms
                            else:
                                break
                        else:
                            error_text = await response.text()
                            logger.warning(f"Binance API returned status {response.status}: {error_text}")
                            break
                    
                    await asyncio.sleep(0.2)  # Rate limiting
            
            return sorted(candles, key=lambda x: x['timestamp'])
            
        except Exception as e:
            logger.error(f"Failed to fetch from Binance: {e}", exc_info=True)
            return []
    
    async def _fetch_batch_coinbase(
        self,
        session: aiohttp.ClientSession,
        pair: str,
        start: datetime,
        end: datetime,
        granularity: int
    ) -> List[Dict]:
        """Fetch a single batch of candles from Coinbase."""
        try:
            url = f"{self.coinbase_url}/products/{pair}/candles"
            # Coinbase Exchange API uses ISO 8601 format with Z suffix and numeric granularity
            params = {
                'start': start.strftime('%Y-%m-%dT%H:%M:%SZ'),
                'end': end.strftime('%Y-%m-%dT%H:%M:%SZ'),
                'granularity': granularity
            }
            
            async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.warning(f"API returned status {response.status} for {pair}: {error_text}")
                    return []
                
                data = await response.json()
                
                # Handle error response
                if isinstance(data, dict) and 'message' in data:
                    logger.warning(f"API error for {pair}: {data.get('message')}")
                    return []
                
                if not isinstance(data, list):
                    logger.warning(f"Unexpected response format for {pair}: {type(data)}")
                    return []
                
                # Convert to our format
                # Coinbase format: [time (Unix seconds), low, high, open, close, volume]
                candles = []
                for candle in data:
                    if len(candle) >= 6:
                        # Handle timestamp - could be seconds or milliseconds
                        timestamp = candle[0]
                        if timestamp > 1e10:  # If > 1e10, it's milliseconds
                            timestamp = timestamp / 1000
                        
                        candles.append({
                            'timestamp': datetime.fromtimestamp(timestamp),
                            'open': float(candle[3]),
                            'high': float(candle[2]),
                            'low': float(candle[1]),
                            'close': float(candle[4]),
                            'volume': float(candle[5])
                        })
                
                return sorted(candles, key=lambda x: x['timestamp'])
                
        except Exception as e:
            logger.error(f"Failed to fetch batch: {e}", exc_info=True)
            return []
    
    async def fetch_days(self, pair: str, days: int, granularity: str = 'ONE_MINUTE') -> List[Dict]:
        """Fetch N days of historical data."""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        return await self.fetch_candles(pair, start_date, end_date, granularity)

