"""EMA + RSI + Volume scalping strategy."""

import logging
from typing import Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
from config import get_config

logger = logging.getLogger(__name__)


class EMARSIStrategy:
    """Trading strategy using EMA, RSI, and volume confirmation."""
    
    def __init__(self, config=None):
        self.config = config or get_config()
        
        # Strategy parameters
        self.ema_period = self.config.EMA_PERIOD
        self.rsi_period = self.config.RSI_PERIOD
        self.volume_period = self.config.VOLUME_PERIOD
        self.volume_multiplier = self.config.VOLUME_MULTIPLIER
        self.min_confidence = self.config.MIN_CONFIDENCE_SCORE
        
        # RSI thresholds
        self.rsi_long_min = self.config.RSI_LONG_MIN
        self.rsi_long_max = self.config.RSI_LONG_MAX
        self.rsi_short_min = self.config.RSI_SHORT_MIN
        self.rsi_short_max = self.config.RSI_SHORT_MAX
        
        logger.info(f"EMARSIStrategy initialized (EMA: {self.ema_period}, RSI: {self.rsi_period})")
    
    def calculate_ema(self, prices: List[float], period: int) -> List[float]:
        """Calculate Exponential Moving Average."""
        if len(prices) < period:
            return []
        
        df = pd.Series(prices)
        ema = df.ewm(span=period, adjust=False).mean()
        return ema.tolist()
    
    def calculate_rsi(self, prices: List[float], period: int) -> List[float]:
        """Calculate Relative Strength Index."""
        if len(prices) < period + 1:
            return []
        
        df = pd.Series(prices)
        delta = df.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi.fillna(50).tolist()
    
    def calculate_volume_avg(self, volumes: List[float], period: int) -> float:
        """Calculate average volume over period."""
        if len(volumes) < period:
            return sum(volumes) / len(volumes) if volumes else 0.0
        
        recent_volumes = volumes[-period:]
        return sum(recent_volumes) / len(recent_volumes)
    
    def calculate_indicators(self, candles: List[Dict]) -> Dict[str, any]:
        """Calculate all technical indicators from candle data."""
        if len(candles) < max(self.ema_period, self.rsi_period, self.volume_period) + 1:
            return {}
        
        # Extract data
        closes = [c['close'] for c in candles]
        volumes = [c['volume'] for c in candles]
        
        # Calculate indicators
        ema_values = self.calculate_ema(closes, self.ema_period)
        rsi_values = self.calculate_rsi(closes, self.rsi_period)
        volume_avg = self.calculate_volume_avg(volumes, self.volume_period)
        
        if not ema_values or not rsi_values:
            return {}
        
        current_price = closes[-1]
        current_ema = ema_values[-1]
        current_rsi = rsi_values[-1]
        current_volume = volumes[-1]
        
        return {
            'price': current_price,
            'ema': current_ema,
            'rsi': current_rsi,
            'volume': current_volume,
            'volume_avg': volume_avg,
            'volume_ratio': current_volume / volume_avg if volume_avg > 0 else 1.0
        }
    
    def calculate_confidence_score(self, indicators: Dict, signal_type: str) -> float:
        """Calculate confidence score for a trading signal."""
        price = indicators['price']
        ema = indicators['ema']
        rsi = indicators['rsi']
        volume_ratio = indicators.get('volume_ratio', 1.0)
        
        confidence = 0.0
        
        if signal_type == 'LONG':
            # Price distance from EMA (0-30%)
            price_distance_pct = ((price - ema) / ema) * 100
            if price_distance_pct > 0:
                price_confidence = min(30.0, (price_distance_pct / 2.0))
            else:
                price_confidence = 0.0
            
            # RSI position in range (0-40%)
            if self.rsi_long_min <= rsi <= self.rsi_long_max:
                rsi_range = self.rsi_long_max - self.rsi_long_min
                rsi_position = (rsi - self.rsi_long_min) / rsi_range
                rsi_confidence = 40.0 * (1 - abs(rsi_position - 0.5) * 2)  # Peak at middle
            else:
                rsi_confidence = 0.0
            
            # Volume confirmation (0-30%)
            if volume_ratio >= self.volume_multiplier:
                volume_confidence = min(30.0, ((volume_ratio - self.volume_multiplier) / self.volume_multiplier) * 30.0)
            else:
                volume_confidence = 0.0
            
            confidence = price_confidence + rsi_confidence + volume_confidence
        
        elif signal_type == 'SHORT':
            # Price distance from EMA (0-30%)
            price_distance_pct = ((ema - price) / ema) * 100
            if price_distance_pct > 0:
                price_confidence = min(30.0, (price_distance_pct / 2.0))
            else:
                price_confidence = 0.0
            
            # RSI position in range (0-40%)
            if self.rsi_short_min <= rsi <= self.rsi_short_max:
                rsi_range = self.rsi_short_max - self.rsi_short_min
                rsi_position = (rsi - self.rsi_short_min) / rsi_range
                rsi_confidence = 40.0 * (1 - abs(rsi_position - 0.5) * 2)  # Peak at middle
            else:
                rsi_confidence = 0.0
            
            # Volume confirmation (0-30%)
            if volume_ratio >= self.volume_multiplier:
                volume_confidence = min(30.0, ((volume_ratio - self.volume_multiplier) / self.volume_multiplier) * 30.0)
            else:
                volume_confidence = 0.0
            
            confidence = price_confidence + rsi_confidence + volume_confidence
        
        return min(100.0, max(0.0, confidence))
    
    def calculate_exit_levels(self, entry_price: float, signal_type: str, confidence: float) -> Tuple[float, float]:
        """Calculate take profit and stop loss levels based on confidence."""
        # Higher confidence = wider take profit, tighter stop loss
        confidence_factor = confidence / 100.0
        
        # Take profit range: 0.15% to 0.40%
        tp_range = self.config.TAKE_PROFIT_MAX - self.config.TAKE_PROFIT_MIN
        take_profit_pct = self.config.TAKE_PROFIT_MIN + (tp_range * confidence_factor)
        
        # Stop loss range: 0.10% to 0.50% (inverse - higher confidence = tighter stop)
        sl_range = self.config.STOP_LOSS_MAX - self.config.STOP_LOSS_MIN
        stop_loss_pct = self.config.STOP_LOSS_MAX - (sl_range * confidence_factor)
        
        if signal_type == 'LONG':
            take_profit = entry_price * (1 + take_profit_pct / 100)
            stop_loss = entry_price * (1 - stop_loss_pct / 100)
        else:  # SHORT
            take_profit = entry_price * (1 - take_profit_pct / 100)
            stop_loss = entry_price * (1 + stop_loss_pct / 100)
        
        return take_profit, stop_loss
    
    def generate_signal(self, candles: List[Dict]) -> Optional[Dict]:
        """Generate trading signal based on indicators."""
        if len(candles) < max(self.ema_period, self.rsi_period, self.volume_period) + 1:
            return None
        
        indicators = self.calculate_indicators(candles)
        if not indicators:
            return None
        
        price = indicators['price']
        ema = indicators['ema']
        rsi = indicators['rsi']
        volume_ratio = indicators['volume_ratio']
        
        signal = None
        confidence = 0.0
        
        # Long entry conditions
        if (price > ema and 
            self.rsi_long_min <= rsi <= self.rsi_long_max and
            volume_ratio >= self.volume_multiplier):
            
            confidence = self.calculate_confidence_score(indicators, 'LONG')
            if confidence >= self.min_confidence:
                take_profit, stop_loss = self.calculate_exit_levels(price, 'LONG', confidence)
                signal = {
                    'type': 'LONG',
                    'price': price,
                    'confidence': confidence,
                    'take_profit': take_profit,
                    'stop_loss': stop_loss,
                    'indicators': indicators
                }
        
        # Short entry conditions
        elif (price < ema and 
              self.rsi_short_min <= rsi <= self.rsi_short_max and
              volume_ratio >= self.volume_multiplier):
            
            confidence = self.calculate_confidence_score(indicators, 'SHORT')
            if confidence >= self.min_confidence:
                take_profit, stop_loss = self.calculate_exit_levels(price, 'SHORT', confidence)
                signal = {
                    'type': 'SHORT',
                    'price': price,
                    'confidence': confidence,
                    'take_profit': take_profit,
                    'stop_loss': stop_loss,
                    'indicators': indicators
                }
        
        return signal
    
    def should_exit(self, position: Dict, current_price: float) -> Tuple[bool, Optional[str]]:
        """Check if position should be exited based on stop loss, take profit, or time."""
        exit_reason = None
        should_exit = False
        
        side = position['side']
        entry_price = position['entry_price']
        stop_loss = position.get('stop_loss')
        take_profit = position.get('take_profit')
        entry_time = position.get('entry_time')
        
        if side == 'LONG':
            # Check stop loss
            if stop_loss and current_price <= stop_loss:
                should_exit = True
                exit_reason = 'STOP_LOSS'
            
            # Check take profit
            elif take_profit and current_price >= take_profit:
                should_exit = True
                exit_reason = 'TAKE_PROFIT'
            
            # Check trailing stop (optional - could be added)
        
        elif side == 'SHORT':
            # Check stop loss
            if stop_loss and current_price >= stop_loss:
                should_exit = True
                exit_reason = 'STOP_LOSS'
            
            # Check take profit
            elif take_profit and current_price <= take_profit:
                should_exit = True
                exit_reason = 'TAKE_PROFIT'
        
        # Check time-based exit (10 minutes)
        if entry_time:
            from datetime import datetime, timedelta
            if isinstance(entry_time, str):
                entry_time = datetime.fromisoformat(entry_time)
            time_elapsed = datetime.utcnow() - entry_time
            if time_elapsed >= timedelta(minutes=self.config.POSITION_TIMEOUT_MINUTES):
                should_exit = True
                exit_reason = 'TIMEOUT'
        
        return should_exit, exit_reason
