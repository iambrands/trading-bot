"""Backtest engine for simulating trading strategy on historical data."""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from config import get_config
from strategy import EMARSIStrategy
from risk import RiskManager
from monitoring import PerformanceTracker

logger = logging.getLogger(__name__)


class BacktestEngine:
    """Simulates trading strategy on historical data."""
    
    def __init__(self, config=None, initial_balance: float = 100000.0):
        self.config = config or get_config()
        self.initial_balance = initial_balance
        self.current_balance = initial_balance
        
        # Initialize components
        self.strategy = EMARSIStrategy(self.config)
        self.risk_manager = RiskManager(self.config)
        self.performance_tracker = PerformanceTracker(self.config)
        
        # Backtest state
        self.positions: List[Dict] = []
        self.trades: List[Dict] = []
        self.equity_curve: List[Dict] = []
        
        logger.info(f"BacktestEngine initialized with ${initial_balance:,.2f}")
    
    def run_backtest(
        self,
        candles: List[Dict],
        pair: str = 'BTC-USD'
    ) -> Dict:
        """
        Run backtest on historical candles.
        
        Args:
            candles: List of historical candle dictionaries
            pair: Trading pair symbol
        
        Returns:
            Backtest results dictionary
        """
        logger.info(f"Starting backtest for {pair} with {len(candles)} candles")
        
        # Reset state
        self.current_balance = self.initial_balance
        self.positions = []
        self.trades = []
        self.equity_curve = []
        self.risk_manager.daily_pnl = 0.0
        
        # Process each candle
        min_candles = max(self.config.EMA_PERIOD, self.config.RSI_PERIOD, self.config.VOLUME_PERIOD) + 1
        
        for i in range(min_candles, len(candles)):
            current_candle = candles[i]
            current_price = current_candle['close']
            current_time = current_candle['timestamp']
            
            # Get historical candles up to this point
            historical_candles = candles[:i+1]
            
            # Manage existing positions
            self._manage_positions(current_price, current_time)
            
            # Check for new signals (only if we have room for positions)
            if len(self.positions) < self.config.MAX_POSITIONS:
                signal = self.strategy.generate_signal(historical_candles)
                
                # Log diagnostic info periodically (every 100 candles) to help debug why no signals
                if i % 100 == 0 and signal is None:
                    indicators = self.strategy.calculate_indicators(historical_candles)
                    if indicators:
                        logger.debug(f"Candle {i}/{len(candles)}: price={current_price:.2f}, "
                                   f"EMA={indicators.get('ema', 0):.2f}, "
                                   f"RSI={indicators.get('rsi', 0):.1f}, "
                                   f"vol_ratio={indicators.get('volume_ratio', 0):.2f}, "
                                   f"signal=None")
                
                if signal:
                    logger.info(f"✅ Signal generated at candle {i}: {signal['type']} @ ${current_price:.2f}, confidence={signal.get('confidence', 0):.1f}%")
                    # Check risk management
                    position_size = self._calculate_position_size(current_price, signal)
                    
                    if position_size > 0:
                        self._open_position(
                            pair,
                            signal,
                            position_size,
                            current_price,
                            current_time
                        )
                    else:
                        logger.debug(f"Signal generated but position_size={position_size}, skipping")
            
            # Update equity curve
            self._update_equity_curve(current_time)
        
        # Close any remaining positions
        final_price = candles[-1]['close'] if candles else 0
        final_time = candles[-1]['timestamp'] if candles else datetime.utcnow()
        for position in self.positions[:]:
            self._close_position(position, final_price, final_time, 'BACKTEST_END')
        
        # Generate results
        results = self._generate_results()
        logger.info(f"Backtest completed: {results['total_trades']} trades, P&L: ${results['total_pnl']:.2f}")
        
        return results
    
    def _calculate_position_size(self, price: float, signal: Dict) -> float:
        """Calculate position size based on risk management."""
        try:
            stop_loss = signal.get('stop_loss', price * 0.99)
            signal_type = signal.get('type', 'LONG')
            
            position_size = self.risk_manager.calculate_position_size(
                self.current_balance,
                price,
                stop_loss,
                signal_type
            )
            
            return position_size
        except Exception as e:
            logger.warning(f"Failed to calculate position size: {e}")
            return 0.0
    
    def _open_position(
        self,
        pair: str,
        signal: Dict,
        size: float,
        entry_price: float,
        entry_time: datetime
    ):
        """Open a new position."""
        try:
            position = {
                'id': len(self.positions) + 1,
                'pair': pair,
                'side': signal['type'],
                'size': size,
                'entry_price': entry_price,
                'stop_loss': signal.get('stop_loss'),
                'take_profit': signal.get('take_profit'),
                'entry_time': entry_time,
                'confidence_score': signal.get('confidence', 0)
            }
            
            self.positions.append(position)
            logger.debug(f"Opened {signal['type']} position: {pair} @ ${entry_price:.2f}")
            
        except Exception as e:
            logger.error(f"Failed to open position: {e}", exc_info=True)
    
    def _manage_positions(self, current_price: float, current_time: datetime):
        """Check exit conditions for open positions."""
        for position in self.positions[:]:
            try:
                # Check stop loss
                if position.get('stop_loss'):
                    if position['side'] == 'LONG' and current_price <= position['stop_loss']:
                        self._close_position(position, current_price, current_time, 'STOP_LOSS')
                        continue
                    elif position['side'] == 'SHORT' and current_price >= position['stop_loss']:
                        self._close_position(position, current_price, current_time, 'STOP_LOSS')
                        continue
                
                # Check take profit
                if position.get('take_profit'):
                    if position['side'] == 'LONG' and current_price >= position['take_profit']:
                        self._close_position(position, current_price, current_time, 'TAKE_PROFIT')
                        continue
                    elif position['side'] == 'SHORT' and current_price <= position['take_profit']:
                        self._close_position(position, current_price, current_time, 'TAKE_PROFIT')
                        continue
                
                # Check strategy exit
                should_exit, exit_reason = self.strategy.should_exit(position, current_price)
                if should_exit:
                    self._close_position(position, current_price, current_time, exit_reason or 'STRATEGY_EXIT')
                    continue
                
                # Check timeout
                if self.risk_manager.check_position_timeout(position):
                    self._close_position(position, current_price, current_time, 'TIMEOUT')
                    continue
                    
            except Exception as e:
                logger.error(f"Error managing position: {e}", exc_info=True)
    
    def _close_position(
        self,
        position: Dict,
        exit_price: float,
        exit_time: datetime,
        exit_reason: str
    ):
        """Close a position and record the trade."""
        try:
            pair = position['pair']
            side = position['side']
            size = position['size']
            entry_price = position['entry_price']
            
            # Calculate P&L
            if side == 'LONG':
                pnl = (exit_price - entry_price) * size
            else:  # SHORT
                pnl = (entry_price - exit_price) * size
            
            # Apply trading fees (0.6% per trade, so 1.2% total for round trip)
            fee_rate = 0.006
            fees = (entry_price * size * fee_rate) + (exit_price * size * fee_rate)
            pnl_after_fees = pnl - fees
            
            pnl_pct = (pnl_after_fees / (entry_price * size)) * 100.0 if entry_price * size > 0 else 0.0
            
            # Update balance
            self.current_balance += pnl_after_fees
            
            # Record trade
            trade = {
                'pair': pair,
                'side': side,
                'entry_price': entry_price,
                'exit_price': exit_price,
                'size': size,
                'entry_time': position['entry_time'],
                'exit_time': exit_time,
                'pnl': pnl_after_fees,
                'pnl_pct': pnl_pct,
                'exit_reason': exit_reason,
                'fees': fees,
                'confidence_score': position.get('confidence_score', 0)
            }
            
            self.trades.append(trade)
            self.positions.remove(position)
            
            # Update performance tracker
            self.performance_tracker.record_trade({
                'pair': pair,
                'side': side,
                'entry_price': entry_price,
                'exit_price': exit_price,
                'size': size,
                'pnl': pnl_after_fees,
                'pnl_pct': pnl_pct,
                'exit_reason': exit_reason,
                'entry_time': position['entry_time'],
                'exit_time': exit_time,
                'confidence_score': position.get('confidence_score', 0)
            })
            
            # Update risk manager
            self.risk_manager.update_daily_pnl(pnl_after_fees)
            
            logger.debug(f"Closed {side} position: {pair} P&L: ${pnl_after_fees:.2f} ({pnl_pct:.2f}%)")
            
        except Exception as e:
            logger.error(f"Failed to close position: {e}", exc_info=True)
    
    def _update_equity_curve(self, timestamp: datetime):
        """Update equity curve with current balance."""
        self.equity_curve.append({
            'timestamp': timestamp,
            'balance': self.current_balance
        })
    
    def _generate_results(self) -> Dict:
        """Generate backtest results summary."""
        total_pnl = sum(trade['pnl'] for trade in self.trades)
        total_fees = sum(trade.get('fees', 0) for trade in self.trades)
        final_balance = self.current_balance
        roi = ((final_balance - self.initial_balance) / self.initial_balance) * 100.0
        
        winning_trades = [t for t in self.trades if t['pnl'] > 0]
        losing_trades = [t for t in self.trades if t['pnl'] < 0]
        
        win_rate = (len(winning_trades) / len(self.trades) * 100.0) if self.trades else 0.0
        avg_win = sum(t['pnl'] for t in winning_trades) / len(winning_trades) if winning_trades else 0.0
        avg_loss = sum(t['pnl'] for t in losing_trades) / len(losing_trades) if losing_trades else 0.0
        
        gross_profit = sum(t['pnl'] for t in winning_trades)
        gross_loss = abs(sum(t['pnl'] for t in losing_trades))
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf') if gross_profit > 0 else 0.0
        
        # Calculate max drawdown
        max_drawdown = 0.0
        peak = self.initial_balance
        for point in self.equity_curve:
            if point['balance'] > peak:
                peak = point['balance']
            drawdown = ((peak - point['balance']) / peak) * 100.0
            if drawdown > max_drawdown:
                max_drawdown = drawdown
        
        # Get performance metrics from tracker
        perf_summary = self.performance_tracker.get_performance_summary(final_balance, self.initial_balance)
        
        return {
            'initial_balance': self.initial_balance,
            'final_balance': final_balance,
            'total_pnl': total_pnl,
            'total_fees': total_fees,
            'roi_pct': roi,
            'total_trades': len(self.trades),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': win_rate,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor,
            'max_drawdown': max_drawdown,
            'trades': self.trades,
            'equity_curve': self.equity_curve,
            'performance': perf_summary
        }

