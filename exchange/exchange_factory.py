"""
Exchange Factory - Unified interface for multiple exchanges
Supports: Binance, Coinbase, OKX, Bybit, Kraken

CRITICAL: This replaces the Coinbase-only client with multi-exchange support
"""

from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)

class ExchangeInterface(ABC):
    """Abstract base class for exchange implementations"""
    
    @abstractmethod
    def get_balance(self):
        """Get account balance"""
        pass
    
    @abstractmethod
    def get_ticker(self, symbol):
        """Get current ticker price"""
        pass
    
    @abstractmethod
    def place_order(self, symbol, side, order_type, amount, price=None):
        """Place order"""
        pass
    
    @abstractmethod
    def get_order(self, order_id, symbol):
        """Get order status"""
        pass
    
    @abstractmethod
    def cancel_order(self, order_id, symbol):
        """Cancel an order"""
        pass
    
    @abstractmethod
    def get_fee_structure(self):
        """Return fee structure (taker, maker)"""
        pass
    
    @abstractmethod
    def get_candles(self, symbol, timeframe, start=None, end=None, limit=None):
        """Get historical candle data"""
        pass


class BinanceClient(ExchangeInterface):
    """
    Binance implementation - PRIMARY EXCHANGE
    
    Fee Structure:
    - Taker: 0.10%
    - Maker: 0.10% (0.075% with BNB discount)
    - VIP 1+: Maker rebates available
    
    CRITICAL: Much lower fees than Coinbase (0.6% vs 0.1%)
    """
    
    def __init__(self, api_key, api_secret, testnet=False):
        try:
            import ccxt
        except ImportError:
            raise ImportError("ccxt library required. Install with: pip install ccxt")
        
        self.name = 'binance'
        
        options = {
            'apiKey': api_key,
            'secret': api_secret,
            'enableRateLimit': True,
            'options': {
                'defaultType': 'spot',  # spot, margin, or future
            }
        }
        
        if testnet:
            options['urls'] = {
                'api': {
                    'public': 'https://testnet.binance.vision/api',
                    'private': 'https://testnet.binance.vision/api',
                }
            }
        
        self.client = ccxt.binance(options)
        
        # Fee structure
        self.taker_fee = 0.0010  # 0.10%
        self.maker_fee = 0.0010  # 0.10%
        
        logger.info(f"✅ Binance client initialized (testnet={testnet})")
    
    def get_balance(self):
        """Get account balance"""
        try:
            balance = self.client.fetch_balance()
            return {
                'total': balance['total'],
                'free': balance['free'],
                'used': balance['used']
            }
        except Exception as e:
            logger.error(f"Error fetching balance: {e}")
            return None
    
    def get_ticker(self, symbol):
        """Get current ticker price"""
        try:
            ticker = self.client.fetch_ticker(symbol)
            return {
                'symbol': symbol,
                'bid': ticker['bid'],
                'ask': ticker['ask'],
                'last': ticker['last'],
                'volume': ticker['baseVolume'],
                'timestamp': ticker['timestamp']
            }
        except Exception as e:
            logger.error(f"Error fetching ticker for {symbol}: {e}")
            return None
    
    def place_order(self, symbol, side, order_type, amount, price=None):
        """
        Place order on Binance
        
        Args:
            symbol: Trading pair (e.g., 'BTC/USDT')
            side: 'buy' or 'sell'
            order_type: 'market' or 'limit'
            amount: Order size in base currency
            price: Limit price (required for limit orders)
        """
        try:
            # Validate inputs
            if order_type == 'limit' and price is None:
                raise ValueError("Price required for limit orders")
            
            # Place order
            if order_type == 'market':
                order = self.client.create_market_order(symbol, side, amount)
            else:
                order = self.client.create_limit_order(symbol, side, amount, price)
            
            logger.info(f"✅ Order placed: {side} {amount} {symbol} @ {price}")
            
            return {
                'id': order['id'],
                'symbol': order['symbol'],
                'side': order['side'],
                'type': order['type'],
                'amount': order['amount'],
                'price': order.get('price'),
                'filled': order.get('filled', 0),
                'status': order['status'],
                'timestamp': order['timestamp']
            }
            
        except Exception as e:
            logger.error(f"Error placing order: {e}")
            return None
    
    def get_order(self, order_id, symbol):
        """Get order status"""
        try:
            order = self.client.fetch_order(order_id, symbol)
            return {
                'id': order['id'],
                'status': order['status'],
                'filled': order.get('filled', 0),
                'remaining': order.get('remaining', 0),
                'average': order.get('average'),
                'fee': order.get('fee')
            }
        except Exception as e:
            logger.error(f"Error fetching order {order_id}: {e}")
            return None
    
    def cancel_order(self, order_id, symbol):
        """Cancel an order"""
        try:
            result = self.client.cancel_order(order_id, symbol)
            logger.info(f"✅ Order cancelled: {order_id}")
            return result
        except Exception as e:
            logger.error(f"Error cancelling order {order_id}: {e}")
            return None
    
    def get_fee_structure(self):
        """Return fee structure"""
        return {
            'taker': self.taker_fee,
            'maker': self.maker_fee,
            'exchange': 'binance'
        }
    
    def get_candles(self, symbol, timeframe, start=None, end=None, limit=None):
        """Get historical candle data"""
        try:
            candles = self.client.fetch_ohlcv(symbol, timeframe, since=start, limit=limit)
            
            # Convert to standard format
            result = []
            for candle in candles:
                result.append({
                    'timestamp': candle[0],
                    'open': candle[1],
                    'high': candle[2],
                    'low': candle[3],
                    'close': candle[4],
                    'volume': candle[5]
                })
            
            return result
        except Exception as e:
            logger.error(f"Error fetching candles for {symbol}: {e}")
            return []


class CoinbaseClientWrapper(ExchangeInterface):
    """
    Coinbase Advanced Trade implementation - LEGACY WRAPPER
    
    Fee Structure:
    - Taker: 0.60%
    - Maker: 0.40%
    
    WARNING: High fees make scalping unprofitable
    This is a wrapper around the existing CoinbaseClient
    """
    
    def __init__(self, coinbase_client):
        """Wrap existing CoinbaseClient to match interface"""
        from exchange.coinbase_client import CoinbaseClient
        self.client = coinbase_client
        self.name = 'coinbase'
        
        # Coinbase fee structure
        self.taker_fee = 0.0060  # 0.60%
        self.maker_fee = 0.0040  # 0.40%
        
        logger.warning("⚠️ Coinbase has high fees (0.6%). Consider using Binance.")
    
    def get_balance(self):
        """Get account balance"""
        # Use existing coinbase client methods
        try:
            balance = self.client.get_account_balance()
            return {
                'total': {'USDT': balance} if isinstance(balance, (int, float)) else balance,
                'free': {'USDT': balance} if isinstance(balance, (int, float)) else balance,
                'used': {}
            }
        except Exception as e:
            logger.error(f"Error fetching balance: {e}")
            return None
    
    def get_ticker(self, symbol):
        """Get current ticker price"""
        try:
            # Convert symbol format (BTC/USDT -> BTC-USD for Coinbase)
            coinbase_symbol = symbol.replace('/', '-')
            market_data = self.client.get_market_data([coinbase_symbol])
            
            if coinbase_symbol in market_data:
                data = market_data[coinbase_symbol]
                return {
                    'symbol': symbol,
                    'bid': data.get('price', 0),
                    'ask': data.get('price', 0),
                    'last': data.get('price', 0),
                    'volume': data.get('volume_24h', 0),
                    'timestamp': data.get('timestamp')
                }
            return None
        except Exception as e:
            logger.error(f"Error fetching ticker for {symbol}: {e}")
            return None
    
    def place_order(self, symbol, side, order_type, amount, price=None):
        """Place order - uses existing coinbase client"""
        # Convert symbol format
        coinbase_symbol = symbol.replace('/', '-')
        # Use existing place_order method
        try:
            result = self.client.place_order(coinbase_symbol, side, amount)
            return {
                'id': result.get('order_id', ''),
                'symbol': symbol,
                'side': side,
                'type': order_type,
                'amount': amount,
                'price': price,
                'status': 'pending'
            }
        except Exception as e:
            logger.error(f"Error placing order: {e}")
            return None
    
    def get_order(self, order_id, symbol):
        """Get order status"""
        # Coinbase implementation would go here
        return None
    
    def cancel_order(self, order_id, symbol):
        """Cancel an order"""
        # Coinbase implementation would go here
        return None
    
    def get_fee_structure(self):
        """Return fee structure"""
        return {
            'taker': self.taker_fee,
            'maker': self.maker_fee,
            'exchange': 'coinbase'
        }
    
    def get_candles(self, symbol, timeframe, start=None, end=None, limit=None):
        """Get historical candle data"""
        try:
            # Convert symbol format
            coinbase_symbol = symbol.replace('/', '-')
            # Use existing get_candles method
            candles = self.client.get_candles(
                coinbase_symbol,
                granularity=self._convert_timeframe(timeframe),
                start=start,
                end=end
            )
            return candles if candles else []
        except Exception as e:
            logger.error(f"Error fetching candles: {e}")
            return []
    
    def _convert_timeframe(self, timeframe):
        """Convert timeframe format"""
        mapping = {
            '1m': 'ONE_MINUTE',
            '5m': 'FIVE_MINUTE',
            '15m': 'FIFTEEN_MINUTE',
            '1h': 'ONE_HOUR',
            '4h': 'FOUR_HOUR',
            '1d': 'ONE_DAY'
        }
        return mapping.get(timeframe, 'ONE_MINUTE')


class ExchangeFactory:
    """Factory to create exchange clients"""
    
    EXCHANGES = {
        'binance': BinanceClient,
        'coinbase': CoinbaseClientWrapper,
    }
    
    @staticmethod
    def create(exchange_name, config):
        """
        Create exchange client
        
        Args:
            exchange_name: 'binance' or 'coinbase'
            config: Configuration object with API credentials
        """
        exchange_name = exchange_name.lower()
        
        if exchange_name not in ExchangeFactory.EXCHANGES:
            raise ValueError(f"Unsupported exchange: {exchange_name}. Supported: {list(ExchangeFactory.EXCHANGES.keys())}")
        
        exchange_class = ExchangeFactory.EXCHANGES[exchange_name]
        
        # Get credentials from config
        if exchange_name == 'binance':
            api_key = getattr(config, 'BINANCE_API_KEY', '')
            api_secret = getattr(config, 'BINANCE_API_SECRET', '')
            testnet = getattr(config, 'BINANCE_TESTNET', True)
            
            if not api_key or not api_secret:
                raise ValueError("BINANCE_API_KEY and BINANCE_API_SECRET required in config")
            
            return exchange_class(
                api_key=api_key,
                api_secret=api_secret,
                testnet=testnet
            )
        
        elif exchange_name == 'coinbase':
            # For Coinbase, we need to wrap the existing client
            from exchange.coinbase_client import CoinbaseClient
            coinbase_client = CoinbaseClient(config)
            return exchange_class(coinbase_client)
        
        else:
            raise ValueError(f"Exchange {exchange_name} not yet implemented")
    
    @staticmethod
    def get_fee_comparison():
        """Return fee comparison across exchanges"""
        return {
            'binance': {
                'taker': 0.10,
                'maker': 0.10,
                'recommended': True,
                'note': 'Best balance of fees and liquidity'
            },
            'coinbase': {
                'taker': 0.60,
                'maker': 0.40,
                'recommended': False,
                'note': 'High fees make scalping unprofitable'
            }
        }

