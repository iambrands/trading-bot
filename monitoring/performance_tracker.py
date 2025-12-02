"""Performance tracking and analytics system."""

import logging
from collections import deque
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import numpy as np
from config import get_config

logger = logging.getLogger(__name__)


class PerformanceTracker:
    """Tracks trading performance metrics."""
    
    def __init__(self, config=None):
        self.config = config or get_config()
        
        # Trade tracking
        self.trades: deque = deque(maxlen=1000)
        self.daily_pnl_history: deque = deque(maxlen=252)  # 1 year of trading days
        self.equity_curve: deque = deque(maxlen=1000)
        
        # Metrics
        self.total_pnl = 0.0
        self.daily_pnl = 0.0
        self.total_trades = 0
        self.winning_trades = 0
        self.losing_trades = 0
        self.gross_profit = 0.0
        self.gross_loss = 0.0
        
        # Daily reset tracking
        self.last_reset_date = datetime.utcnow().date()
        
        logger.info("PerformanceTracker initialized")
    
    def reset_daily_metrics(self):
        """Reset daily metrics at start of new day."""
        now = datetime.utcnow().date()
        if now > self.last_reset_date:
            # Save yesterday's metrics
            if self.last_reset_date:
                self.daily_pnl_history.append({
                    'date': self.last_reset_date,
                    'daily_pnl': self.daily_pnl,
                    'total_trades': self._get_daily_trade_count(self.last_reset_date)
                })
            
            # Reset daily metrics
            self.daily_pnl = 0.0
            self.last_reset_date = now
            logger.info("Daily performance metrics reset")
    
    def _get_daily_trade_count(self, date: datetime.date) -> int:
        """Get trade count for a specific date."""
        count = 0
        for trade in self.trades:
            trade_date = trade.get('exit_time')
            if trade_date:
                if isinstance(trade_date, str):
                    trade_date = datetime.fromisoformat(trade_date).date()
                elif isinstance(trade_date, datetime):
                    trade_date = trade_date.date()
                else:
                    continue
                
                if trade_date == date:
                    count += 1
        return count
    
    def record_trade(self, trade_data: Dict):
        """Record a completed trade."""
        self.reset_daily_metrics()
        
        pnl = trade_data.get('pnl', 0.0)
        pnl_pct = trade_data.get('pnl_pct', 0.0)
        
        # Update metrics
        self.total_pnl += pnl
        self.daily_pnl += pnl
        self.total_trades += 1
        
        if pnl > 0:
            self.winning_trades += 1
            self.gross_profit += pnl
        elif pnl < 0:
            self.losing_trades += 1
            self.gross_loss += abs(pnl)
        
        # Store trade
        trade_record = {
            'id': trade_data.get('id'),
            'pair': trade_data.get('pair'),
            'side': trade_data.get('side'),
            'entry_price': trade_data.get('entry_price'),
            'exit_price': trade_data.get('exit_price'),
            'size': trade_data.get('size'),
            'pnl': pnl,
            'pnl_pct': pnl_pct,
            'exit_reason': trade_data.get('exit_reason'),
            'entry_time': trade_data.get('entry_time'),
            'exit_time': trade_data.get('exit_time'),
            'confidence_score': trade_data.get('confidence_score')
        }
        
        self.trades.append(trade_record)
        logger.debug(f"Trade recorded: {trade_record['pair']} {trade_record['side']} "
                    f"P&L: ${pnl:.2f} ({pnl_pct:.2f}%)")
    
    def update_equity_curve(self, account_balance: float):
        """Update equity curve with current account balance."""
        self.equity_curve.append({
            'timestamp': datetime.utcnow(),
            'balance': account_balance
        })
    
    def calculate_win_rate(self) -> float:
        """Calculate win rate percentage."""
        if self.total_trades == 0:
            return 0.0
        return (self.winning_trades / self.total_trades) * 100.0
    
    def calculate_profit_factor(self) -> float:
        """Calculate profit factor (gross profit / gross loss)."""
        if self.gross_loss == 0:
            return float('inf') if self.gross_profit > 0 else 0.0
        return self.gross_profit / self.gross_loss
    
    def calculate_average_win(self) -> float:
        """Calculate average winning trade."""
        if self.winning_trades == 0:
            return 0.0
        return self.gross_profit / self.winning_trades
    
    def calculate_average_loss(self) -> float:
        """Calculate average losing trade."""
        if self.losing_trades == 0:
            return 0.0
        return self.gross_loss / self.losing_trades
    
    def calculate_expectancy(self) -> float:
        """Calculate expectancy per trade."""
        if self.total_trades == 0:
            return 0.0
        win_rate = self.winning_trades / self.total_trades
        avg_win = self.calculate_average_win()
        avg_loss = self.calculate_average_loss()
        return (win_rate * avg_win) - ((1 - win_rate) * avg_loss)
    
    def calculate_sharpe_ratio(self, risk_free_rate: float = 0.0) -> float:
        """Calculate Sharpe ratio (risk-adjusted returns)."""
        if len(self.daily_pnl_history) < 2:
            return 0.0
        
        daily_returns = [d['daily_pnl'] for d in self.daily_pnl_history]
        if len(daily_returns) < 2:
            return 0.0
        
        returns_array = np.array(daily_returns)
        mean_return = np.mean(returns_array)
        std_return = np.std(returns_array)
        
        if std_return == 0:
            return 0.0
        
        # Annualized Sharpe ratio (assuming 252 trading days)
        sharpe = (mean_return - risk_free_rate / 252) / std_return * np.sqrt(252)
        return sharpe
    
    def calculate_max_drawdown(self, initial_balance: float) -> float:
        """Calculate maximum drawdown percentage."""
        if len(self.equity_curve) < 2:
            return 0.0
        
        balances = [point['balance'] for point in self.equity_curve]
        if not balances:
            return 0.0
        
        peak = balances[0]
        max_dd = 0.0
        
        for balance in balances:
            if balance > peak:
                peak = balance
            drawdown = (peak - balance) / peak * 100.0
            if drawdown > max_dd:
                max_dd = drawdown
        
        return max_dd
    
    def get_performance_summary(self, account_balance: float, initial_balance: float) -> Dict:
        """Get complete performance summary."""
        self.reset_daily_metrics()
        
        win_rate = self.calculate_win_rate()
        profit_factor = self.calculate_profit_factor()
        sharpe_ratio = self.calculate_sharpe_ratio()
        max_drawdown = self.calculate_max_drawdown(initial_balance)
        avg_win = self.calculate_average_win()
        avg_loss = self.calculate_average_loss()
        expectancy = self.calculate_expectancy()
        
        # Calculate return on investment
        roi = ((account_balance - initial_balance) / initial_balance) * 100.0 if initial_balance > 0 else 0.0
        
        return {
            'account_balance': account_balance,
            'initial_balance': initial_balance,
            'total_pnl': self.total_pnl,
            'daily_pnl': self.daily_pnl,
            'roi_pct': roi,
            'total_trades': self.total_trades,
            'winning_trades': self.winning_trades,
            'losing_trades': self.losing_trades,
            'win_rate': win_rate,
            'profit_factor': profit_factor,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'average_win': avg_win,
            'average_loss': avg_loss,
            'expectancy': expectancy,
            'gross_profit': self.gross_profit,
            'gross_loss': self.gross_loss,
            'meets_targets': {
                'win_rate': win_rate >= self.config.TARGET_WIN_RATE,
                'profit_factor': profit_factor >= self.config.TARGET_PROFIT_FACTOR,
                'sharpe_ratio': sharpe_ratio >= self.config.TARGET_SHARPE_RATIO,
                'max_drawdown': max_drawdown <= self.config.TARGET_MAX_DRAWDOWN
            }
        }
    
    def get_recent_trades(self, limit: int = 50) -> List[Dict]:
        """Get recent trades."""
        return list(self.trades)[-limit:]
    
    def get_equity_curve(self, limit: int = 1000) -> List[Dict]:
        """Get equity curve data."""
        return list(self.equity_curve)[-limit:]
