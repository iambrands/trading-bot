"""Risk management system for position sizing and limits."""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from config import get_config

logger = logging.getLogger(__name__)


class RiskManager:
    """Manages risk limits and position sizing."""
    
    def __init__(self, config=None):
        self.config = config or get_config()
        
        # Risk parameters
        self.risk_per_trade_pct = self.config.RISK_PER_TRADE_PCT
        self.max_positions = self.config.MAX_POSITIONS
        self.daily_loss_limit = self.config.DAILY_LOSS_LIMIT
        self.max_position_size_pct = self.config.MAX_POSITION_SIZE_PCT
        self.max_position_size_usdt = getattr(self.config, 'MAX_POSITION_SIZE_USDT', 500.0)  # Hard cap in USD
        self.position_timeout_minutes = self.config.POSITION_TIMEOUT_MINUTES
        
        # Tracking
        self.daily_pnl = 0.0
        self.daily_reset_time = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        
        logger.info("RiskManager initialized")
    
    def reset_daily_metrics(self):
        """Reset daily metrics at start of new day."""
        now = datetime.utcnow()
        if now.date() > self.daily_reset_time.date():
            self.daily_pnl = 0.0
            self.daily_reset_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
            logger.info("Daily risk metrics reset")
    
    def calculate_position_size(self, account_balance: float, entry_price: float, 
                               stop_loss_price: float, signal_type: str) -> float:
        """Calculate position size based on risk parameters."""
        # Risk amount per trade
        risk_amount = account_balance * (self.risk_per_trade_pct / 100.0)
        
        # Price difference for stop loss
        if signal_type == 'LONG':
            price_diff = entry_price - stop_loss_price
        else:  # SHORT
            price_diff = stop_loss_price - entry_price
        
        if price_diff <= 0:
            logger.warning(f"Invalid stop loss: entry={entry_price}, stop={stop_loss_price}")
            return 0.0
        
        # Calculate position size
        position_size = risk_amount / price_diff
        
        # Cap at maximum position size percentage
        max_position_value = account_balance * (self.max_position_size_pct / 100.0)
        max_position_size = max_position_value / entry_price
        
        position_size = min(position_size, max_position_size)
        
        logger.debug(f"Position size calculated: {position_size:.6f} (risk: ${risk_amount:.2f}, "
                    f"price_diff: ${price_diff:.2f})")
        
        return position_size
    
    def validate_trade(self, account_balance: float, positions: List[Dict], 
                      new_position_size: float, entry_price: float) -> Tuple[bool, str]:
        """Validate if a new trade can be opened."""
        self.reset_daily_metrics()
        
        # Check daily loss limit
        if self.daily_pnl <= -self.daily_loss_limit:
            return False, f"Daily loss limit reached: ${self.daily_pnl:.2f}"
        
        # Check max positions
        if len(positions) >= self.max_positions:
            return False, f"Maximum positions limit reached: {len(positions)}/{self.max_positions}"
        
        # Check position size
        position_value = new_position_size * entry_price
        position_pct = (position_value / account_balance) * 100.0
        
        if position_pct > self.max_position_size_pct:
            return False, f"Position size too large: {position_pct:.2f}% > {self.max_position_size_pct}%"
        
        # Check total exposure
        total_exposure = sum(p.get('size', 0) * p.get('entry_price', 0) for p in positions)
        total_exposure += position_value
        exposure_pct = (total_exposure / account_balance) * 100.0
        
        if exposure_pct > 100.0:
            return False, f"Total exposure too high: {exposure_pct:.2f}%"
        
        # Check if daily loss would exceed limit with worst case
        remaining_daily_capacity = self.daily_loss_limit + self.daily_pnl
        risk_per_trade = account_balance * (self.risk_per_trade_pct / 100.0)
        
        if remaining_daily_capacity < risk_per_trade:
            return False, f"Insufficient daily risk capacity: ${remaining_daily_capacity:.2f}"
        
        return True, "Trade validated"
    
    def update_daily_pnl(self, pnl: float):
        """Update daily P&L tracking."""
        self.reset_daily_metrics()
        self.daily_pnl += pnl
        logger.debug(f"Daily P&L updated: ${self.daily_pnl:.2f}")
    
    def get_risk_metrics(self, account_balance: float, positions: List[Dict]) -> Dict:
        """Get current risk exposure metrics."""
        self.reset_daily_metrics()
        
        total_exposure = sum(p.get('size', 0) * p.get('entry_price', 0) for p in positions)
        total_exposure_pct = (total_exposure / account_balance) * 100.0 if account_balance > 0 else 0.0
        
        # Calculate risk exposure (distance to stop loss)
        total_risk = 0.0
        for position in positions:
            size = position.get('size', 0)
            entry_price = position.get('entry_price', 0)
            stop_loss = position.get('stop_loss', 0)
            side = position.get('side', 'LONG')
            
            if stop_loss > 0:
                if side == 'LONG':
                    risk_per_unit = entry_price - stop_loss
                else:
                    risk_per_unit = stop_loss - entry_price
                total_risk += size * risk_per_unit
        
        risk_exposure_pct = (total_risk / account_balance) * 100.0 if account_balance > 0 else 0.0
        
        remaining_daily_capacity = self.daily_loss_limit + self.daily_pnl
        remaining_positions = self.max_positions - len(positions)
        
        return {
            'total_exposure': total_exposure,
            'total_exposure_pct': total_exposure_pct,
            'risk_exposure': total_risk,
            'risk_exposure_pct': risk_exposure_pct,
            'daily_pnl': self.daily_pnl,
            'daily_loss_limit': self.daily_loss_limit,
            'remaining_daily_capacity': remaining_daily_capacity,
            'open_positions': len(positions),
            'max_positions': self.max_positions,
            'remaining_positions': remaining_positions,
            'daily_loss_limit_reached': self.daily_pnl <= -self.daily_loss_limit
        }
    
    def check_position_timeout(self, position: Dict) -> bool:
        """Check if position has exceeded timeout."""
        entry_time = position.get('entry_time')
        if not entry_time:
            return False
        
        if isinstance(entry_time, str):
            entry_time = datetime.fromisoformat(entry_time)
        
        time_elapsed = datetime.utcnow() - entry_time
        return time_elapsed >= timedelta(minutes=self.position_timeout_minutes)
    
    def should_close_all_positions(self) -> bool:
        """Check if all positions should be closed (daily loss limit)."""
        self.reset_daily_metrics()
        return self.daily_pnl <= -self.daily_loss_limit
