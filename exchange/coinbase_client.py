"""Coinbase Advanced Trade API client with paper trading support."""

import asyncio
import base64
import hashlib
import hmac
import json
import logging
import random
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import aiohttp
import websockets
from config import get_config

logger = logging.getLogger(__name__)


class CoinbaseClient:
    """Coinbase Advanced Trade API client."""
    
    def __init__(self, config=None):
        self.config = config or get_config()
        self.api_key = self.config.COINBASE_API_KEY
        self.api_secret = self.config.COINBASE_API_SECRET
        self.passphrase = self.config.COINBASE_API_PASSPHRASE
        self.base_url = self.config.COINBASE_API_URL
        self.ws_url = self.config.COINBASE_WS_URL
        self.paper_trading = self.config.PAPER_TRADING
        
        # Paper trading state
        self.paper_balance = self.config.ACCOUNT_SIZE
        self.paper_positions: Dict[str, Dict] = {}
        self.paper_orders: Dict[str, Dict] = {}
        
        # WebSocket connection
        self.ws_connection = None
        self.ws_task = None
        self.market_data: Dict[str, Dict] = {}
        
        # Session for HTTP requests
        self.session: Optional[aiohttp.ClientSession] = None
        
        logger.info(f"CoinbaseClient initialized (Paper Trading: {self.paper_trading})")
    
    def _generate_signature(self, timestamp: str, method: str, path: str, body: str = '') -> str:
        """Generate Coinbase API signature."""
        message = f"{timestamp}{method}{path}{body}"
        hmac_key = base64.b64decode(self.api_secret)
        signature = hmac.new(hmac_key, message.encode(), hashlib.sha256)
        return base64.b64encode(signature.digest()).decode()
    
    async def _make_request(self, method: str, endpoint: str, params: Optional[Dict] = None, data: Optional[Dict] = None) -> Dict:
        """Make authenticated API request."""
        if self.paper_trading:
            return await self._paper_request(method, endpoint, params, data)
        
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        path = f"/api/v3/brokerage{endpoint}"
        url = f"https://api.coinbase.com{path}"
        timestamp = str(int(time.time()))
        body = json.dumps(data) if data else ''
        
        headers = {
            'CB-ACCESS-KEY': self.api_key,
            'CB-ACCESS-SIGN': self._generate_signature(timestamp, method, path, body),
            'CB-ACCESS-TIMESTAMP': timestamp,
            'CB-ACCESS-PASSPHRASE': self.passphrase,
            'Content-Type': 'application/json'
        }
        
        try:
            async with self.session.request(method, url, headers=headers, params=params, json=data) as response:
                result = await response.json()
                if response.status >= 400:
                    logger.error(f"API error: {response.status} - {result}")
                    raise Exception(f"API error: {result}")
                return result
        except Exception as e:
            logger.error(f"Request failed: {e}", exc_info=True)
            raise
    
    async def _paper_request(self, method: str, endpoint: str, params: Optional[Dict] = None, data: Optional[Dict] = None) -> Dict:
        """Simulate API request in paper trading mode."""
        # Simulate network delay
        await asyncio.sleep(0.01 + random.random() * 0.02)
        
        if endpoint == '/accounts' and method == 'GET':
            return {
                'accounts': [{
                    'uuid': 'paper-account',
                    'name': 'Paper Trading Account',
                    'currency': 'USD',
                    'available_balance': {'value': str(self.paper_balance)}
                }]
            }
        
        elif endpoint.startswith('/products') and method == 'GET':
            pair = params.get('product_id', 'BTC-USD') if params else 'BTC-USD'
            current_price = self.market_data.get(pair, {}).get('price', 50000.0)
            return {
                'product_id': pair,
                'price': str(current_price),
                'volume_24h': str(random.uniform(1000000, 5000000))
            }
        
        elif endpoint == '/orders' and method == 'POST':
            return await self._paper_place_order(data)
        
        elif '/orders/' in endpoint and method == 'DELETE':
            order_id = endpoint.split('/orders/')[-1]
            return await self._paper_cancel_order(order_id)
        
        return {}
    
    async def _paper_place_order(self, order_data: Dict) -> Dict:
        """Simulate order placement in paper trading."""
        pair = order_data['product_id']
        side = order_data['side']
        order_config = order_data['order_configuration']['market_market_ioc']
        size = float(order_config.get('quote_size' if side == 'BUY' else 'base_size', 0))
        
        # Get current market price
        current_price = self.market_data.get(pair, {}).get('price', 50000.0)
        if not current_price:
            current_price = 50000.0 if 'BTC' in pair else 3000.0
        
        # Apply slippage
        slippage = random.uniform(self.config.PAPER_SLIPPAGE_MIN, self.config.PAPER_SLIPPAGE_MAX)
        if side == 'BUY':
            fill_price = current_price * (1 + slippage / 100)
            cost = size  # quote_size in USD
            base_size = cost / fill_price
        else:
            fill_price = current_price * (1 - slippage / 100)
            base_size = size  # base_size in crypto
            cost = base_size * fill_price
        
        # Apply fees
        fee = cost * self.config.PAPER_FEE_RATE
        total_cost = cost + fee if side == 'BUY' else cost - fee
        
        # Check balance
        if side == 'BUY' and total_cost > self.paper_balance:
            raise Exception(f"Insufficient balance. Need ${total_cost:.2f}, have ${self.paper_balance:.2f}")
        
        if side == 'SELL':
            # Check if we have the position
            if pair not in self.paper_positions or self.paper_positions[pair]['size'] < base_size:
                raise Exception(f"Insufficient position size for {pair}")
        
        # Update paper balance and positions
        order_id = f"paper-{int(time.time() * 1000)}-{random.randint(1000, 9999)}"
        
        if side == 'BUY':
            self.paper_balance -= total_cost
            if pair in self.paper_positions:
                # Average cost calculation
                old_size = self.paper_positions[pair]['size']
                old_avg_price = self.paper_positions[pair]['avg_price']
                new_avg_price = (old_size * old_avg_price + base_size * fill_price) / (old_size + base_size)
                self.paper_positions[pair]['size'] += base_size
                self.paper_positions[pair]['avg_price'] = new_avg_price
            else:
                self.paper_positions[pair] = {
                    'size': base_size,
                    'avg_price': fill_price
                }
        else:
            self.paper_balance += cost - fee
            self.paper_positions[pair]['size'] -= base_size
            if self.paper_positions[pair]['size'] <= 0:
                del self.paper_positions[pair]
        
        self.paper_orders[order_id] = {
            'order_id': order_id,
            'product_id': pair,
            'side': side,
            'order_configuration': order_data['order_configuration'],
            'status': 'FILLED',
            'fill_price': fill_price,
            'fill_size': base_size,
            'created_time': datetime.utcnow().isoformat()
        }
        
        logger.info(f"Paper order executed: {side} {base_size:.6f} {pair} @ ${fill_price:.2f}")
        
        return {
            'order_id': order_id,
            'product_id': pair,
            'side': side,
            'order_configuration': order_data['order_configuration'],
            'order_status': 'FILLED',
            'success': True
        }
    
    async def _paper_cancel_order(self, order_id: str) -> Dict:
        """Simulate order cancellation in paper trading."""
        if order_id in self.paper_orders:
            del self.paper_orders[order_id]
            return {'order_id': order_id, 'success': True}
        return {'order_id': order_id, 'success': False, 'error': 'Order not found'}
    
    async def get_account_balance(self) -> float:
        """Get USD account balance."""
        try:
            if self.paper_trading:
                return self.paper_balance
            
            result = await self._make_request('GET', '/accounts')
            for account in result.get('accounts', []):
                if account.get('currency') == 'USD':
                    return float(account.get('available_balance', {}).get('value', 0))
            return 0.0
        except Exception as e:
            logger.error(f"Failed to get account balance: {e}", exc_info=True)
            return 0.0
    
    async def _fetch_real_market_data(self, pair: str) -> Optional[Dict]:
        """Fetch real market data from Coinbase public API."""
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        try:
            # Use Coinbase public API endpoint (no authentication required)
            url = f"https://api.exchange.coinbase.com/products/{pair}/ticker"
            async with self.session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        'price': float(data.get('price', 0)),
                        'volume_24h': float(data.get('volume_24h', 0)),
                        'timestamp': datetime.utcnow()
                    }
        except Exception as e:
            logger.debug(f"Public API fetch failed for {pair}, trying authenticated endpoint: {e}")
            # Fall back to authenticated endpoint if API keys are available
            if self.api_key and self.api_secret:
                try:
                    product_data = await self._make_request('GET', '/products/' + pair)
                    if product_data:
                        return {
                            'price': float(product_data.get('price', 0)),
                            'volume_24h': float(product_data.get('volume_24h', 0)),
                            'timestamp': datetime.utcnow()
                        }
                except Exception as e2:
                    logger.debug(f"Authenticated endpoint also failed for {pair}: {e2}")
        return None
    
    async def get_market_data(self, pairs: List[str]) -> Dict[str, Dict]:
        """Get current prices and volume for trading pairs."""
        result = {}
        use_real_data = self.config.USE_REAL_MARKET_DATA or not self.paper_trading
        
        for pair in pairs:
            try:
                if use_real_data:
                    # Try to fetch real market data
                    real_data = await self._fetch_real_market_data(pair)
                    if real_data:
                        self.market_data[pair] = real_data
                        result[pair] = real_data.copy()
                        continue
                    else:
                        logger.debug(f"Could not fetch real data for {pair}, using cached or synthetic data (this is normal for paper trading or unavailable pairs)")
                
                # Fall back to cached data or generate synthetic
                if pair in self.market_data:
                    result[pair] = self.market_data[pair].copy()
                else:
                    # Generate synthetic prices as last resort
                    base_price = 50000.0 if 'BTC' in pair else 3000.0
                    self.market_data[pair] = {
                        'price': base_price,
                        'volume_24h': random.uniform(1000000, 5000000),
                        'timestamp': datetime.utcnow()
                    }
                    result[pair] = self.market_data[pair].copy()
            except Exception as e:
                logger.error(f"Failed to get market data for {pair}: {e}", exc_info=True)
                result[pair] = {'price': 0, 'volume_24h': 0, 'timestamp': datetime.utcnow()}
        
        return result
    
    async def place_order(self, pair: str, side: str, size: float, quote_size: Optional[float] = None) -> Dict:
        """Place a market order."""
        if quote_size:
            # Buying with USD
            order_config = {
                'market_market_ioc': {
                    'quote_size': str(quote_size)
                }
            }
        else:
            # Selling with base currency
            order_config = {
                'market_market_ioc': {
                    'base_size': str(size)
                }
            }
        
        order_data = {
            'product_id': pair,
            'side': side,
            'order_configuration': order_config
        }
        
        try:
            result = await self._make_request('POST', '/orders', data=order_data)
            return result
        except Exception as e:
            logger.error(f"Failed to place order: {e}", exc_info=True)
            raise
    
    async def cancel_order(self, order_id: str) -> bool:
        """Cancel an order."""
        try:
            result = await self._make_request('DELETE', f'/orders/{order_id}')
            return result.get('success', False)
        except Exception as e:
            logger.error(f"Failed to cancel order {order_id}: {e}", exc_info=True)
            return False
    
    async def _fetch_real_candles(self, pair: str, granularity: str, start: datetime, end: datetime) -> List[Dict]:
        """Fetch real historical candle data from Coinbase."""
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        try:
            # Use Coinbase public API for candles
            # Granularity mapping: ONE_MINUTE=60, FIVE_MINUTE=300, FIFTEEN_MINUTE=900, etc.
            granularity_map = {
                'ONE_MINUTE': 60,
                'FIVE_MINUTE': 300,
                'FIFTEEN_MINUTE': 900,
                'ONE_HOUR': 3600,
                'SIX_HOUR': 21600,
                'ONE_DAY': 86400
            }
            granularity_seconds = granularity_map.get(granularity, 60)
            
            url = f"https://api.exchange.coinbase.com/products/{pair}/candles"
            params = {
                'start': start.strftime('%Y-%m-%dT%H:%M:%SZ'),
                'end': end.strftime('%Y-%m-%dT%H:%M:%SZ'),
                'granularity': granularity_seconds
            }
            
            async with self.session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    data = await response.json()
                    if not data or (isinstance(data, dict) and 'message' in data):
                        # API returned error, try without date params (get recent data)
                        params_simple = {'granularity': granularity_seconds}
                        async with self.session.get(url, params=params_simple, timeout=aiohttp.ClientTimeout(total=10)) as resp2:
                            if resp2.status == 200:
                                data = await resp2.json()
                    
                    candles = []
                    if isinstance(data, list):
                        for candle in data:
                            # Coinbase format: [time, low, high, open, close, volume]
                            if len(candle) >= 6:
                                candles.append({
                                    'timestamp': int(candle[0]),
                                    'low': float(candle[1]),
                                    'high': float(candle[2]),
                                    'open': float(candle[3]),
                                    'close': float(candle[4]),
                                    'volume': float(candle[5])
                                })
                    return sorted(candles, key=lambda x: x['timestamp']) if candles else []
        except Exception as e:
            logger.debug(f"Public API candles fetch failed for {pair}: {e}")
            # Try authenticated endpoint if available
            if self.api_key and self.api_secret:
                try:
                    params = {
                        'product_id': pair,
                        'granularity': granularity,
                        'start': int(start.timestamp()),
                        'end': int(end.timestamp())
                    }
                    result = await self._make_request('GET', '/products/' + pair + '/candles', params=params)
                    candles = []
                    for candle in result.get('candles', []):
                        candles.append({
                            'timestamp': int(candle[0]),
                            'low': float(candle[1]),
                            'high': float(candle[2]),
                            'open': float(candle[3]),
                            'close': float(candle[4]),
                            'volume': float(candle[5])
                        })
                    return sorted(candles, key=lambda x: x['timestamp'])
                except Exception as e2:
                    logger.debug(f"Authenticated candles endpoint also failed: {e2}")
        return []
    
    async def get_candles(self, pair: str, granularity: str = 'ONE_MINUTE', start: Optional[datetime] = None, end: Optional[datetime] = None) -> List[Dict]:
        """Get historical candle data."""
        if not start:
            start = datetime.utcnow() - timedelta(hours=24)
        if not end:
            end = datetime.utcnow()
        
        try:
            use_real_data = self.config.USE_REAL_MARKET_DATA or not self.paper_trading
            
            if use_real_data:
                # Try to fetch real candles
                real_candles = await self._fetch_real_candles(pair, granularity, start, end)
                if real_candles:
                    logger.debug(f"Fetched {len(real_candles)} real candles for {pair}")
                    return real_candles
                else:
                    logger.debug(f"Could not fetch real candles for {pair}, generating synthetic data (this is normal for paper trading or unavailable pairs)")
            
            # Try to get current price before generating synthetic candles
            # This ensures synthetic candles start from current price, not old defaults
            try:
                current_market = await self.get_market_data([pair])
                if pair in current_market and 'price' in current_market[pair]:
                    base_price = float(current_market[pair]['price'])
                    logger.debug(f"Using current price ${base_price:.2f} as base for synthetic candles ({pair})")
            except Exception as e:
                logger.debug(f"Could not fetch current price for synthetic candles: {e}")
            
            # Fall back to synthetic candles
            return self._generate_synthetic_candles(pair, start, end, granularity)
        except Exception as e:
            logger.error(f"Failed to get candles for {pair}: {e}", exc_info=True)
            return []
    
    def _generate_synthetic_candles(self, pair: str, start: datetime, end: datetime, granularity: str) -> List[Dict]:
        """Generate synthetic candle data for paper trading."""
        # Try to get current real-time price, fall back to defaults if unavailable
        base_price = None
        try:
            # Use real-time price if available in market_data
            if hasattr(self, 'market_data') and pair in self.market_data:
                market_info = self.market_data[pair]
                if isinstance(market_info, dict) and 'price' in market_info:
                    base_price = float(market_info['price'])
                    logger.debug(f"Using current real-time price ${base_price:.2f} as base for synthetic candles ({pair})")
        except Exception as e:
            logger.debug(f"Could not get real-time price for synthetic candles: {e}")
        
        # Fall back to defaults if real-time price not available
        if base_price is None or base_price <= 0:
            base_price = 50000.0 if 'BTC' in pair else 3000.0
            logger.debug(f"Using default base price ${base_price:.2f} for synthetic candles ({pair})")
        
        candles = []
        current_time = start
        current_price = base_price
        
        while current_time < end:
            # Random walk price movement
            change_pct = random.uniform(-0.5, 0.5)
            current_price *= (1 + change_pct / 100)
            
            candle = {
                'timestamp': int(current_time.timestamp()),
                'open': current_price,
                'high': current_price * (1 + random.uniform(0, 0.3) / 100),
                'low': current_price * (1 - random.uniform(0, 0.3) / 100),
                'close': current_price,
                'volume': random.uniform(100000, 500000)
            }
            candle['close'] = random.uniform(candle['low'], candle['high'])
            candles.append(candle)
            current_price = candle['close']
            
            # Increment time based on granularity
            if granularity == 'ONE_MINUTE':
                current_time += timedelta(minutes=1)
            elif granularity == 'FIVE_MINUTE':
                current_time += timedelta(minutes=5)
            elif granularity == 'FIFTEEN_MINUTE':
                current_time += timedelta(minutes=15)
            else:
                current_time += timedelta(minutes=1)
        
        return candles
    
    async def start_websocket(self, pairs: List[str]):
        """Start WebSocket connection for real-time market data."""
        use_real_data = self.config.USE_REAL_MARKET_DATA or not self.paper_trading
        
        if use_real_data and (self.api_key or not self.paper_trading):
            # Use real WebSocket connection
            self.ws_task = asyncio.create_task(self._websocket_loop(pairs))
        else:
            # Use paper trading data generator or public ticker updates
            self.ws_task = asyncio.create_task(self._paper_websocket_loop(pairs))
            
            # If using real market data but no auth, poll public API periodically
            if use_real_data and not self.api_key:
                asyncio.create_task(self._poll_real_market_data(pairs))
    
    async def _poll_real_market_data(self, pairs: List[str]):
        """Poll public API for real market data updates."""
        while True:
            try:
                await asyncio.sleep(5)  # Update every 5 seconds
                for pair in pairs:
                    real_data = await self._fetch_real_market_data(pair)
                    if real_data:
                        self.market_data[pair] = real_data
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error polling market data: {e}", exc_info=True)
                await asyncio.sleep(10)
    
    async def _websocket_loop(self, pairs: List[str]):
        """WebSocket loop for live trading."""
        try:
            async with websockets.connect(self.ws_url) as ws:
                self.ws_connection = ws
                # Subscribe to ticker channels
                subscribe_msg = {
                    'type': 'subscribe',
                    'product_ids': pairs,
                    'channels': ['ticker']
                }
                await ws.send(json.dumps(subscribe_msg))
                
                async for message in ws:
                    data = json.loads(message)
                    if data.get('type') == 'ticker':
                        pair = data.get('product_id')
                        self.market_data[pair] = {
                            'price': float(data.get('price', 0)),
                            'volume_24h': float(data.get('volume_24h', 0)),
                            'timestamp': datetime.utcnow()
                        }
        except Exception as e:
            logger.error(f"WebSocket error: {e}", exc_info=True)
            await asyncio.sleep(5)
            # Attempt reconnection
            await self.start_websocket(pairs)
    
    async def _paper_websocket_loop(self, pairs: List[str]):
        """Simulated WebSocket loop for paper trading."""
        logger.info("Starting paper trading WebSocket simulation")
        while True:
            try:
                await asyncio.sleep(1)  # Update every second
                for pair in pairs:
                    if pair not in self.market_data:
                        base_price = 50000.0 if 'BTC' in pair else 3000.0
                        self.market_data[pair] = {
                            'price': base_price,
                            'volume_24h': random.uniform(1000000, 5000000),
                            'timestamp': datetime.utcnow()
                        }
                    else:
                        # Simulate price movement
                        change_pct = random.uniform(-0.1, 0.1)
                        self.market_data[pair]['price'] *= (1 + change_pct / 100)
                        self.market_data[pair]['timestamp'] = datetime.utcnow()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Paper WebSocket error: {e}", exc_info=True)
                await asyncio.sleep(1)
    
    async def stop_websocket(self):
        """Stop WebSocket connection."""
        if self.ws_task:
            self.ws_task.cancel()
            try:
                await self.ws_task
            except asyncio.CancelledError:
                pass
        
        if self.ws_connection:
            await self.ws_connection.close()
        
        logger.info("WebSocket connection stopped")
    
    async def close(self):
        """Close client connections."""
        await self.stop_websocket()
        if self.session:
            await self.session.close()
        logger.info("CoinbaseClient closed")
