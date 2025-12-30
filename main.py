"""Main trading bot orchestrator."""

import asyncio
import logging
import os
import signal
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from config import get_config
from exchange import CoinbaseClient
from strategy import EMARSIStrategy
from risk import RiskManager
from database import DatabaseManager
from monitoring import PerformanceTracker
from alerts import AlertManager
from orders import AdvancedOrderManager
from api.rest_api import create_app, run_api
from utils.log_buffer import setup_log_buffer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('tradingbot.log'),
        logging.StreamHandler(sys.stdout),
        setup_log_buffer(max_size=1000)  # Keep last 1000 log entries in memory
    ]
)

logger = logging.getLogger(__name__)


class TradingBot:
    """Main trading bot orchestrator."""
    
    def __init__(self):
        self.config = get_config()
        
        # Core components
        self.exchange = CoinbaseClient(self.config)
        self.strategy = EMARSIStrategy(self.config)
        self.risk_manager = RiskManager(self.config)
        self.db = DatabaseManager(self.config)
        self.performance_tracker = PerformanceTracker(self.config)
        self.alert_manager = AlertManager(self.config)
        self.order_manager = AdvancedOrderManager(self.exchange, self.config)
        
        # Grid trading components
        from grid_trading import GridTradingManager, DCAManager
        self.grid_manager = GridTradingManager(self.exchange, self.config)
        self.dca_manager = DCAManager(self.exchange, self.config)
        
        # State
        self.status = 'stopped'  # stopped, running, paused
        self.positions: List[Dict] = []
        self.initial_balance = self.config.ACCOUNT_SIZE
        self.running = False
        self.trading_task: Optional[asyncio.Task] = None
        self.api_task: Optional[asyncio.Task] = None
        self.kill_switch_activated = False
        
        # Candle data cache
        self.candle_cache: Dict[str, List[Dict]] = {}
        
        # Daily summary tracking
        self.last_summary_date = datetime.utcnow().date()
        self.daily_summary_sent = False
        
        logger.info("TradingBot initialized")
    
    async def initialize(self):
        """Initialize all components."""
        logger.info("Initializing trading bot components...")
        
        try:
            # Initialize database
            await self.db.initialize()
            
            # Initialize exchange connection
            await self.exchange.start_websocket(self.config.TRADING_PAIRS)
            
            # Load initial balance
            self.initial_balance = await self.exchange.get_account_balance()
            if self.initial_balance == 0:
                self.initial_balance = self.config.ACCOUNT_SIZE
                if self.config.PAPER_TRADING:
                    self.exchange.paper_balance = self.initial_balance
            
            logger.info(f"Initial balance: ${self.initial_balance:.2f}")
            logger.info(f"Paper trading: {self.config.PAPER_TRADING}")
            
            # Load initial candle data
            await self._load_candle_data()
            
            # Start advanced order monitoring
            await self.order_manager.start_monitoring()
            
            # Start grid trading monitoring
            await self.grid_manager.start_monitoring()
            await self.dca_manager.start_monitoring()
            
            logger.info("All components initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize bot: {e}", exc_info=True)
            # Send critical error alert
            try:
                await self.alert_manager.send_error_alert(str(e), 'Bot Initialization')
            except Exception as alert_error:
                logger.warning(f"Failed to send error alert: {alert_error}")
            return False
    
    async def reload_trading_pairs(self):
        """Reload trading pairs dynamically without restarting the bot."""
        logger.info(f"🔄 Reloading trading pairs: {self.config.TRADING_PAIRS}")
        
        try:
            # Stop current WebSocket connection
            if self.exchange.ws and not self.exchange.ws.closed:
                logger.info("Stopping current WebSocket connection...")
                await self.exchange.stop_websocket()
            
            # Restart WebSocket with new pairs
            logger.info(f"Starting WebSocket with new pairs: {self.config.TRADING_PAIRS}")
            await self.exchange.start_websocket(self.config.TRADING_PAIRS)
            
            # Reload candle data for all pairs
            logger.info("Reloading candle data for all trading pairs...")
            await self._load_candle_data()
            
            logger.info(f"✅ Trading pairs reloaded successfully: {self.config.TRADING_PAIRS}")
        except Exception as e:
            logger.error(f"❌ Failed to reload trading pairs: {e}", exc_info=True)
            raise
    
    async def _load_candle_data(self):
        """Load initial candle data for all trading pairs."""
        logger.info("Loading candle data...")
        
        for pair in self.config.TRADING_PAIRS:
            try:
                candles = await self.exchange.get_candles(
                    pair,
                    granularity='ONE_MINUTE',
                    start=datetime.utcnow() - timedelta(hours=24),
                    end=datetime.utcnow()
                )
                self.candle_cache[pair] = candles
                logger.debug(f"Loaded {len(candles)} candles for {pair}")
            except Exception as e:
                logger.error(f"Failed to load candles for {pair}: {e}", exc_info=True)
                self.candle_cache[pair] = []
    
    async def start(self):
        """Start the trading bot."""
        if self.status == 'running':
            logger.warning("Bot is already running")
            return
        
        logger.info("Starting trading bot...")
        
        if not self.running:
            await self.initialize()
        
        self.status = 'running'
        self.running = True
        self.kill_switch_activated = False
        
        # Start trading loop
        self.trading_task = asyncio.create_task(self._trading_loop())
        
        logger.info("Trading bot started")
    
    async def stop(self):
        """Stop the trading bot."""
        logger.info("Stopping trading bot...")
        
        self.status = 'stopped'
        self.running = False
        
        if self.trading_task:
            self.trading_task.cancel()
            try:
                await self.trading_task
            except asyncio.CancelledError:
                pass
        
        # Stop advanced order monitoring
        await self.order_manager.stop_monitoring()
        
        # Stop grid trading monitoring
        await self.grid_manager.stop_monitoring()
        await self.dca_manager.stop_monitoring()
        
        logger.info("Trading bot stopped")
    
    async def kill_switch(self):
        """Emergency kill switch - stop bot and close all positions."""
        logger.critical("KILL SWITCH ACTIVATED")
        self.kill_switch_activated = True
        
        # Close all positions immediately
        await self.close_all_positions()
        
        # Stop the bot
        await self.stop()
    
    async def close_all_positions(self) -> int:
        """Close all open positions."""
        closed_count = 0
        
        for position in self.positions[:]:
            try:
                await self._close_position(position, 'MANUAL_CLOSE')
                closed_count += 1
            except Exception as e:
                logger.error(f"Failed to close position {position.get('id')}: {e}", exc_info=True)
        
        return closed_count
    
    async def _trading_loop(self):
        """Main trading loop."""
        logger.info("Trading loop started")
        
        while self.running and not self.kill_switch_activated:
            try:
                # Update candle data periodically
                if len(self.candle_cache.get(self.config.TRADING_PAIRS[0], [])) < 100:
                    await self._update_candle_data()
                
                # Check and manage existing positions
                await self._manage_positions()
                
                # Check daily loss limit
                if self.risk_manager.should_close_all_positions():
                    logger.warning("Daily loss limit reached - closing all positions")
                    daily_pnl = self.risk_manager.daily_pnl
                    await self.close_all_positions()
                    self.status = 'paused'
                    await self.db.log_event('WARNING', 'Daily loss limit reached')
                    # Send risk alert
                    try:
                        await self.alert_manager.send_risk_alert(
                            f"Daily loss limit reached!\n\n"
                            f"Daily P&L: ${daily_pnl:.2f}\n"
                            f"Limit: ${self.config.DAILY_LOSS_LIMIT:.2f}\n"
                            f"All positions have been closed and bot is paused."
                        )
                    except Exception as alert_error:
                        logger.warning(f"Failed to send risk alert: {alert_error}")
                    continue
                
                # Generate new signals only if running (not paused)
                if self.status == 'running':
                    await self._check_signals()
                
                # Update performance metrics
                balance = await self.exchange.get_account_balance()
                self.performance_tracker.update_equity_curve(balance)
                
                # Check if we should send daily summary (at end of trading day)
                await self._check_daily_summary()
                
                # Wait before next iteration
                await asyncio.sleep(self.config.LOOP_INTERVAL_SECONDS)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in trading loop: {e}", exc_info=True)
                # Send error alert
                try:
                    await self.alert_manager.send_error_alert(str(e), 'Trading Loop')
                except Exception as alert_error:
                    logger.warning(f"Failed to send error alert: {alert_error}")
                await asyncio.sleep(self.config.LOOP_INTERVAL_SECONDS)
        
        logger.info("Trading loop ended")
    
    async def _check_daily_summary(self):
        """Check if we should send daily summary at end of trading day."""
        try:
            current_date = datetime.utcnow().date()
            current_hour = datetime.utcnow().hour
            
            # Send summary at 23:30 (end of trading day)
            # Only send once per day
            if (current_date > self.last_summary_date or 
                (current_hour == 23 and datetime.utcnow().minute >= 30)) and not self.daily_summary_sent:
                
                # Get daily metrics
                daily_pnl = self.performance_tracker.daily_pnl
                total_trades = self.performance_tracker.total_trades
                win_rate = self.performance_tracker.calculate_win_rate()
                
                # Send daily summary
                try:
                    await self.alert_manager.send_daily_summary({
                        'daily_pnl': daily_pnl,
                        'total_trades': total_trades,
                        'win_rate': win_rate,
                        'date': current_date.isoformat()
                    })
                    self.daily_summary_sent = True
                    self.last_summary_date = current_date
                    logger.info("Daily summary sent")
                except Exception as e:
                    logger.warning(f"Failed to send daily summary: {e}")
            
            # Reset daily summary flag at start of new day
            if current_date > self.last_summary_date and current_hour < 1:
                self.daily_summary_sent = False
                
        except Exception as e:
            logger.warning(f"Error checking daily summary: {e}")
    
    async def _update_candle_data(self):
        """Update candle data cache."""
        try:
            for pair in self.config.TRADING_PAIRS:
                # Get latest candle
                candles = await self.exchange.get_candles(
                    pair,
                    granularity='ONE_MINUTE',
                    start=datetime.utcnow() - timedelta(hours=1),
                    end=datetime.utcnow()
                )
                
                if candles:
                    # Merge with existing cache
                    existing = self.candle_cache.get(pair, [])
                    existing_dict = {c['timestamp']: c for c in existing}
                    
                    for candle in candles:
                        existing_dict[candle['timestamp']] = candle
                    
                    # Sort by timestamp and keep last 200
                    sorted_candles = sorted(existing_dict.values(), key=lambda x: x['timestamp'])
                    self.candle_cache[pair] = sorted_candles[-200:]
        except Exception as e:
            logger.error(f"Failed to update candle data: {e}", exc_info=True)
            # Send error alert for API failures
            try:
                await self.alert_manager.send_error_alert(str(e), 'Market Data API')
            except Exception as alert_error:
                logger.warning(f"Failed to send error alert: {alert_error}")
    
    async def _check_signals(self):
        """Check for new trading signals."""
        balance = await self.exchange.get_account_balance()
        
        # Force refresh market data for latest prices
        await self.exchange.get_market_data(self.config.TRADING_PAIRS)
        
        for pair in self.config.TRADING_PAIRS:
            try:
                candles = self.candle_cache.get(pair, [])
                if len(candles) < max(self.config.EMA_PERIOD, self.config.RSI_PERIOD, self.config.VOLUME_PERIOD) + 1:
                    continue
                
                # Use latest ticker price instead of last candle close if available
                market_data = await self.exchange.get_market_data([pair])
                if pair in market_data and market_data[pair].get('price'):
                    # Update last candle with real-time price
                    if candles:
                        candles[-1] = candles[-1].copy()
                        candles[-1]['close'] = market_data[pair]['price']
                        candles[-1]['high'] = max(candles[-1].get('high', market_data[pair]['price']), market_data[pair]['price'])
                        candles[-1]['low'] = min(candles[-1].get('low', market_data[pair]['price']), market_data[pair]['price'])
                
                # Generate signal
                signal = self.strategy.generate_signal(candles)
                
                if signal and signal['confidence'] >= self.config.MIN_CONFIDENCE_SCORE:
                    # Check if we already have a position in this pair
                    existing_position = next((p for p in self.positions if p['pair'] == pair), None)
                    if existing_position:
                        continue
                    
                    # Validate trade with risk manager
                    position_size = self.risk_manager.calculate_position_size(
                        balance,
                        signal['price'],
                        signal['stop_loss'],
                        signal['type']
                    )
                    
                    is_valid, message = self.risk_manager.validate_trade(
                        balance,
                        self.positions,
                        position_size,
                        signal['price']
                    )
                    
                    if is_valid:
                        await self._open_position(pair, signal, position_size)
                    else:
                        logger.debug(f"Trade validation failed for {pair}: {message}")
            
            except Exception as e:
                logger.error(f"Error checking signals for {pair}: {e}", exc_info=True)
    
    async def _open_position(self, pair: str, signal: Dict, size: float):
        """Open a new position."""
        try:
            logger.info(f"Opening {signal['type']} position: {pair} size={size:.6f} @ ${signal['price']:.2f}")
            
            # Place order
            side = 'BUY' if signal['type'] == 'LONG' else 'SELL'
            
            if signal['type'] == 'LONG':
                quote_size = size * signal['price']  # USD amount
                order_result = await self.exchange.place_order(pair, side, 0, quote_size)
            else:
                order_result = await self.exchange.place_order(pair, side, size)
            
            order_id = order_result.get('order_id')
            
            if not order_id:
                logger.error(f"Failed to place order for {pair}")
                return
            
            # Create position record
            position = {
                'id': len(self.positions) + 1,
                'pair': pair,
                'side': signal['type'],
                'size': size,
                'entry_price': signal['price'],
                'stop_loss': signal['stop_loss'],
                'take_profit': signal['take_profit'],
                'entry_time': datetime.utcnow(),
                'order_id': order_id,
                'confidence_score': signal['confidence']
            }
            
            self.positions.append(position)
            
            # Save to database
            trade_data = {
                'pair': pair,
                'side': signal['type'],
                'entry_price': signal['price'],
                'size': size,
                'stop_loss': signal['stop_loss'],
                'take_profit': signal['take_profit'],
                'order_id': order_id,
                'confidence_score': signal['confidence']
            }
            
            trade_id = await self.db.save_trade(trade_data)
            position['db_id'] = trade_id
            
            logger.info(f"Position opened: {pair} {signal['type']} (ID: {trade_id})")
            
            # Send trade alert
            try:
                await self.alert_manager.send_trade_alert({
                    'pair': pair,
                    'side': signal['type'],
                    'entry_price': signal['price'],
                    'size': size,
                    'pnl': 0
                })
            except Exception as e:
                logger.warning(f"Failed to send trade alert: {e}")
            await self.db.log_event('INFO', f'Position opened: {pair} {signal["type"]}', trade_data)
            
        except Exception as e:
            logger.error(f"Failed to open position for {pair}: {e}", exc_info=True)
            # Send error alert for order placement failures
            try:
                await self.alert_manager.send_error_alert(
                    f"Failed to open position for {pair}: {str(e)}", 
                    'Order Execution'
                )
            except Exception as alert_error:
                logger.warning(f"Failed to send error alert: {alert_error}")
    
    async def _manage_positions(self):
        """Manage existing positions - check exit conditions."""
        market_data = await self.exchange.get_market_data(self.config.TRADING_PAIRS)
        
        for position in self.positions[:]:
            try:
                pair = position['pair']
                current_price = market_data.get(pair, {}).get('price', position['entry_price'])
                
                # Check exit conditions
                should_exit, exit_reason = self.strategy.should_exit(position, current_price)
                
                # Check timeout
                if not should_exit:
                    should_exit = self.risk_manager.check_position_timeout(position)
                    if should_exit:
                        exit_reason = 'TIMEOUT'
                
                if should_exit:
                    await self._close_position(position, exit_reason)
            
            except Exception as e:
                logger.error(f"Error managing position {position.get('id')}: {e}", exc_info=True)
    
    async def _close_position(self, position: Dict, exit_reason: str):
        """Close a position."""
        try:
            pair = position['pair']
            side = position['side']
            size = position['size']
            
            logger.info(f"Closing position: {pair} {side} (Reason: {exit_reason})")
            
            # Get current price
            market_data = await self.exchange.get_market_data([pair])
            current_price = market_data.get(pair, {}).get('price', position['entry_price'])
            
            # Place opposite order
            order_side = 'SELL' if side == 'LONG' else 'BUY'
            
            if side == 'LONG':
                order_result = await self.exchange.place_order(pair, order_side, size)
            else:
                quote_size = size * current_price
                order_result = await self.exchange.place_order(pair, order_side, 0, quote_size)
            
            # Calculate P&L
            entry_price = position['entry_price']
            if side == 'LONG':
                pnl = (current_price - entry_price) * size
            else:
                pnl = (entry_price - current_price) * size
            
            pnl_pct = (pnl / (entry_price * size)) * 100.0
            
            # Remove from positions
            self.positions.remove(position)
            
            # Update risk manager
            self.risk_manager.update_daily_pnl(pnl)
            
            # Update performance tracker
            trade_data = {
                'id': position.get('db_id'),
                'pair': pair,
                'side': side,
                'entry_price': entry_price,
                'exit_price': current_price,
                'size': size,
                'pnl': pnl,
                'pnl_pct': pnl_pct,
                'exit_reason': exit_reason,
                'exit_time': datetime.utcnow(),
                'entry_time': position.get('entry_time'),
                'confidence_score': position.get('confidence_score')
            }
            
            self.performance_tracker.record_trade(trade_data)
            
            # Update database
            if position.get('db_id'):
                await self.db.update_trade(position['db_id'], {
                    'exit_price': current_price,
                    'exit_time': datetime.utcnow(),
                    'pnl': pnl,
                    'pnl_pct': pnl_pct,
                    'exit_reason': exit_reason
                })
            
            logger.info(f"Position closed: {pair} {side} P&L: ${pnl:.2f} ({pnl_pct:.2f}%)")
            await self.db.log_event('INFO', f'Position closed: {pair} {side}', {
                'pnl': pnl,
                'pnl_pct': pnl_pct,
                'exit_reason': exit_reason
            })
            
            # Send trade completion alert
            try:
                await self.alert_manager.send_trade_alert({
                    'pair': pair,
                    'side': side,
                    'entry_price': position['entry_price'],
                    'size': position['size'],
                    'pnl': pnl
                })
            except Exception as e:
                logger.warning(f"Failed to send trade alert: {e}")
            
        except Exception as e:
            logger.error(f"Failed to close position: {e}", exc_info=True)
    
    async def run_api_server(self):
        """Run REST API server."""
        try:
            # IMPORTANT (Railway/Heroku):
            # Many PaaS providers require binding to the port provided via $PORT.
            # If we bind to a fixed port (e.g. 4000), the process may be "up" but unreachable.
            port = int(os.environ.get('PORT', self.config.API_PORT))
            logger.info(f"Starting API server on {self.config.API_HOST}:{port}")
            from api.rest_api import create_app, run_api
            app = create_app(bot_instance=self, db_manager=self.db)
            await run_api(app, self.config.API_HOST, port)
        except Exception as e:
            logger.error(f"Failed to start API server: {e}", exc_info=True)
            # Send critical error alert
            try:
                await self.alert_manager.send_error_alert(str(e), 'API Server')
            except Exception as alert_error:
                logger.warning(f"Failed to send error alert: {alert_error}")
            raise


async def main():
    """Main entry point."""
    bot = TradingBot()
    
    # Setup signal handlers
    def signal_handler(signum, frame):
        logger.info("Received shutdown signal")
        asyncio.create_task(bot.stop())
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Initialize bot
        if not await bot.initialize():
            logger.error("Failed to initialize bot")
            return
        
        # Start trading bot
        await bot.start()
        
        # Start API server (after bot is started)
        api_task = asyncio.create_task(bot.run_api_server())
        logger.info("API server task created")
        
        # Keep running
        try:
            await asyncio.gather(
                bot.trading_task,
                api_task,
                return_exceptions=True
            )
        except asyncio.CancelledError:
            pass
    
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
    finally:
        await bot.stop()
        await bot.exchange.close()
        await bot.db.close()
        logger.info("Trading bot shutdown complete")


if __name__ == '__main__':
    asyncio.run(main())
