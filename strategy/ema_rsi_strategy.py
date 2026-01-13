"""EMA + RSI + Volume scalping strategy."""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
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
        
        # Signal tracking for monitoring
        self.signals_generated_today = 0
        self.near_misses_today = 0
        self.candles_analyzed_today = 0
        self.last_summary_date = datetime.now().date()
        self.rsi_values_today: List[float] = []
        self.volume_ratios_today: List[float] = []
        
        logger.info(f"EMARSIStrategy initialized (EMA: {self.ema_period}, RSI: {self.rsi_period})")
        logger.info(f"  RSI Long: {self.rsi_long_min}-{self.rsi_long_max}, RSI Short: {self.rsi_short_min}-{self.rsi_short_max}")
        logger.info(f"  Volume Multiplier: {self.volume_multiplier}x, Min Confidence: {self.min_confidence}%")
    
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
            return sum(volumes) / len(volumes) if volumes else 1.0
        return sum(volumes[-period:]) / period
    
    def calculate_indicators(self, candles: List[Dict]) -> Optional[Dict]:
        """Calculate all technical indicators from candles."""
        if len(candles) < max(self.ema_period, self.rsi_period, self.volume_period):
            return None
        
        prices = [c['close'] for c in candles]
        volumes = [c.get('volume', 0) for c in candles]
        
        # EMA
        ema_values = self.calculate_ema(prices, self.ema_period)
        if not ema_values:
            return None
        ema = ema_values[-1]
        
        # RSI
        rsi_values = self.calculate_rsi(prices, self.rsi_period)
        if not rsi_values:
            return None
        rsi = rsi_values[-1]
        
        # Volume
        volume_avg = self.calculate_volume_avg(volumes, self.volume_period)
        current_volume = volumes[-1] if volumes else 1.0
        
        return {
            'price': prices[-1],
            'ema': ema,
            'rsi': rsi,
            'volume_ratio': current_volume / volume_avg if volume_avg > 0 else 1.0
        }
    
    def calculate_confidence_score(self, indicators: Dict, signal_type: str) -> float:
        """Calculate confidence score for a trading signal."""
        price = indicators['price']
        ema = indicators['ema']
        rsi = indicators['rsi']
        volume_ratio = indicators.get('volume_ratio', 1.0)
        
        confidence = 0.0
        
        # EMA alignment (30 points)
        if signal_type == 'LONG':
            if price > ema:
                ema_distance_pct = ((price - ema) / ema) * 100
                confidence += min(30.0, ema_distance_pct * 10)
        else:  # SHORT
            if price < ema:
                ema_distance_pct = ((ema - price) / ema) * 100
                confidence += min(30.0, ema_distance_pct * 10)
        
        # RSI position (40 points)
        if signal_type == 'LONG':
            if self.rsi_long_min <= rsi <= self.rsi_long_max:
                rsi_range = self.rsi_long_max - self.rsi_long_min
                rsi_position = (rsi - self.rsi_long_min) / rsi_range
                rsi_confidence = 40.0 * (1 - abs(rsi_position - 0.5) * 2)  # Peak at middle
            else:
                rsi_confidence = 0.0
        else:  # SHORT
            if self.rsi_short_min <= rsi <= self.rsi_short_max:
                rsi_range = self.rsi_short_max - self.rsi_short_min
                rsi_position = (rsi - self.rsi_short_min) / rsi_range
                rsi_confidence = 40.0 * (1 - abs(rsi_position - 0.5) * 2)  # Peak at middle
            else:
                rsi_confidence = 0.0
        
        confidence += rsi_confidence
        
        # Volume confirmation (30 points)
        if volume_ratio >= self.volume_multiplier:
            volume_confidence = min(30.0, ((volume_ratio - self.volume_multiplier) / self.volume_multiplier) * 30.0)
        else:
            volume_confidence = 0.0
        
        confidence += volume_confidence
        
        return min(100.0, max(0.0, confidence))
    
    def calculate_exit_levels(self, entry_price: float, signal_type: str, confidence: float) -> Tuple[float, float]:
        """Calculate take profit and stop loss levels based on confidence."""
        # Higher confidence = wider take profit, tighter stop loss
        confidence_factor = confidence / 100.0
        
        # Take profit range: 0.50% to 0.75%
        tp_range = self.config.TAKE_PROFIT_MAX - self.config.TAKE_PROFIT_MIN
        take_profit_pct = self.config.TAKE_PROFIT_MIN + (tp_range * confidence_factor)
        
        # Stop loss range: 0.25% to 0.50% (inverse - higher confidence = tighter stop)
        sl_range = self.config.STOP_LOSS_MAX - self.config.STOP_LOSS_MIN
        stop_loss_pct = self.config.STOP_LOSS_MAX - (sl_range * confidence_factor)
        
        if signal_type == 'LONG':
            take_profit = entry_price * (1 + take_profit_pct / 100)
            stop_loss = entry_price * (1 - stop_loss_pct / 100)
        else:  # SHORT
            take_profit = entry_price * (1 - take_profit_pct / 100)
            stop_loss = entry_price * (1 + stop_loss_pct / 100)
        
        return take_profit, stop_loss
    
    def _log_signal_check(self, price: float, ema: float, rsi: float, volume_ratio: float, pair: str = ""):
        """Log signal check with distance to thresholds for monitoring."""
        pair_label = f"[{pair}] " if pair else ""
        
        # Calculate distances to thresholds
        rsi_long_dist_low = self.rsi_long_min - rsi if rsi < self.rsi_long_min else 0
        rsi_long_dist_high = rsi - self.rsi_long_max if rsi > self.rsi_long_max else 0
        rsi_long_gap = max(rsi_long_dist_low, rsi_long_dist_high)
        
        rsi_short_dist_low = self.rsi_short_min - rsi if rsi < self.rsi_short_min else 0
        rsi_short_dist_high = rsi - self.rsi_short_max if rsi > self.rsi_short_max else 0
        rsi_short_gap = max(rsi_short_dist_low, rsi_short_dist_high)
        
        vol_gap = self.volume_multiplier - volume_ratio if volume_ratio < self.volume_multiplier else 0
        
        # Determine which direction we're checking
        price_above_ema = price > ema
        direction = "LONG" if price_above_ema else "SHORT"
        
        if price_above_ema:
            rsi_in_range = self.rsi_long_min <= rsi <= self.rsi_long_max
            rsi_gap = rsi_long_gap
            rsi_range_str = f"{self.rsi_long_min}-{self.rsi_long_max}"
        else:
            rsi_in_range = self.rsi_short_min <= rsi <= self.rsi_short_max
            rsi_gap = rsi_short_gap
            rsi_range_str = f"{self.rsi_short_min}-{self.rsi_short_max}"
        
        # Log signal check
        logger.debug(
            f"{pair_label}Signal check ({direction}) | "
            f"RSI: {rsi:.2f} (need {rsi_range_str}, gap: {rsi_gap:.2f}) | "
            f"Vol: {volume_ratio:.2f}x (need {self.volume_multiplier}x, gap: {vol_gap:.2f}x) | "
            f"Price>EMA: {price_above_ema}"
        )
        
        # Track near-misses (within 5% of threshold or very close)
        is_near_miss = False
        near_miss_reasons = []
        
        if price_above_ema:  # Checking LONG
            if 0 < rsi_long_gap <= 3:  # Within 3 points of RSI range
                is_near_miss = True
                near_miss_reasons.append(f"RSI gap: {rsi_long_gap:.2f} points")
            if 0 < vol_gap <= 0.15:  # Within 0.15x of volume requirement
                is_near_miss = True
                near_miss_reasons.append(f"Volume gap: {vol_gap:.2f}x")
        else:  # Checking SHORT
            if 0 < rsi_short_gap <= 3:
                is_near_miss = True
                near_miss_reasons.append(f"RSI gap: {rsi_short_gap:.2f} points")
            if 0 < vol_gap <= 0.15:
                is_near_miss = True
                near_miss_reasons.append(f"Volume gap: {vol_gap:.2f}x")
        
        if is_near_miss and near_miss_reasons:
            self.near_misses_today += 1
            logger.warning(
                f"{pair_label}⚠️ NEAR MISS ({direction}): Almost triggered signal | "
                f"{', '.join(near_miss_reasons)} | "
                f"RSI: {rsi:.2f}, Vol: {volume_ratio:.2f}x"
            )
        
        # Track for daily summary
        self.candles_analyzed_today += 1
        self.rsi_values_today.append(rsi)
        self.volume_ratios_today.append(volume_ratio)
    
    def generate_signal(self, candles: List[Dict], pair: str = "") -> Optional[Dict]:
        """Generate trading signal based on indicators."""
        import sys
        
        if len(candles) < max(self.ema_period, self.rsi_period, self.volume_period) + 1:
            return None
        
        indicators = self.calculate_indicators(candles)
        if not indicators:
            return None
        
        price = indicators['price']
        ema = indicators['ema']
        rsi = indicators['rsi']
        volume_ratio = indicators['volume_ratio']
        
        # Diagnostic logging - show actual values
        print(f"    [{pair}] Strategy eval: Price=${price:.2f}, EMA=${ema:.2f}, RSI={rsi:.1f}, Vol={volume_ratio:.2f}x", file=sys.stderr, flush=True)
        
        # Log signal check for monitoring
        self._log_signal_check(price, ema, rsi, volume_ratio, pair)
        
        signal = None
        confidence = 0.0
        
        # Long entry conditions
        long_price_ok = price > ema
        long_rsi_ok = self.rsi_long_min <= rsi <= self.rsi_long_max
        long_volume_ok = volume_ratio >= self.volume_multiplier
        
        print(f"    [{pair}] LONG conditions: Price>EMA={long_price_ok} ({price:.2f}>{ema:.2f}), RSI_in_range={long_rsi_ok} (RSI={rsi:.1f}, need {self.rsi_long_min}-{self.rsi_long_max}), Volume_ok={long_volume_ok} (Vol={volume_ratio:.2f}x, need {self.volume_multiplier}x)", file=sys.stderr, flush=True)
        
        if long_price_ok and long_rsi_ok and long_volume_ok:
            confidence = self.calculate_confidence_score(indicators, 'LONG')
            print(f"    [{pair}] LONG all conditions met! Confidence={confidence:.1f}% (min={self.min_confidence}%)", file=sys.stderr, flush=True)
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
                self.signals_generated_today += 1
                print(f"    [{pair}] ✅✅✅ LONG SIGNAL GENERATED! Confidence={confidence:.1f}%", file=sys.stderr, flush=True)
                logger.info(
                    f"[{pair}] ✅ LONG signal generated: RSI={rsi:.2f} ({self.rsi_long_min}-{self.rsi_long_max}), "
                    f"Vol={volume_ratio:.2f}x (need {self.volume_multiplier}x), Confidence={confidence:.1f}%"
                )
            else:
                gap = self.min_confidence - confidence
                print(f"    [{pair}] LONG confidence too low: {confidence:.1f}% < {self.min_confidence}% (gap: {gap:.1f}%)", file=sys.stderr, flush=True)
        else:
            failed_conditions = []
            if not long_price_ok:
                failed_conditions.append(f"Price>EMA (Price ${price:.2f} <= EMA ${ema:.2f})")
            if not long_rsi_ok:
                failed_conditions.append(f"RSI range (RSI {rsi:.1f} not in {self.rsi_long_min}-{self.rsi_long_max})")
            if not long_volume_ok:
                failed_conditions.append(f"Volume (Vol {volume_ratio:.2f}x < {self.volume_multiplier}x)")
            print(f"    [{pair}] LONG conditions NOT met: {', '.join(failed_conditions)}", file=sys.stderr, flush=True)
        
        # Short entry conditions
        if signal is None:  # Only check short if long didn't trigger
            short_price_ok = price < ema
            short_rsi_ok = self.rsi_short_min <= rsi <= self.rsi_short_max
            short_volume_ok = volume_ratio >= self.volume_multiplier
            
            print(f"    [{pair}] SHORT conditions: Price<EMA={short_price_ok} ({price:.2f}<{ema:.2f}), RSI_in_range={short_rsi_ok} (RSI={rsi:.1f}, need {self.rsi_short_min}-{self.rsi_short_max}), Volume_ok={short_volume_ok} (Vol={volume_ratio:.2f}x, need {self.volume_multiplier}x)", file=sys.stderr, flush=True)
            
            if short_price_ok and short_rsi_ok and short_volume_ok:
                confidence = self.calculate_confidence_score(indicators, 'SHORT')
                print(f"    [{pair}] SHORT all conditions met! Confidence={confidence:.1f}% (min={self.min_confidence}%)", file=sys.stderr, flush=True)
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
                    self.signals_generated_today += 1
                    print(f"    [{pair}] ✅✅✅ SHORT SIGNAL GENERATED! Confidence={confidence:.1f}%", file=sys.stderr, flush=True)
                    logger.info(
                        f"[{pair}] ✅ SHORT signal generated: RSI={rsi:.2f} ({self.rsi_short_min}-{self.rsi_short_max}), "
                        f"Vol={volume_ratio:.2f}x (need {self.volume_multiplier}x), Confidence={confidence:.1f}%"
                    )
                else:
                    gap = self.min_confidence - confidence
                    print(f"    [{pair}] SHORT confidence too low: {confidence:.1f}% < {self.min_confidence}% (gap: {gap:.1f}%)", file=sys.stderr, flush=True)
            else:
                failed_conditions = []
                if not short_price_ok:
                    failed_conditions.append(f"Price<EMA (Price ${price:.2f} >= EMA ${ema:.2f})")
                if not short_rsi_ok:
                    failed_conditions.append(f"RSI range (RSI {rsi:.1f} not in {self.rsi_short_min}-{self.rsi_short_max})")
                if not short_volume_ok:
                    failed_conditions.append(f"Volume (Vol {volume_ratio:.2f}x < {self.volume_multiplier}x)")
                print(f"    [{pair}] SHORT conditions NOT met: {', '.join(failed_conditions)}", file=sys.stderr, flush=True)
        
        if signal is None:
            print(f"    [{pair}] ➖ No signal - returning None", file=sys.stderr, flush=True)
        
        return signal
    
    def log_daily_summary(self):
        """Log daily summary of signal generation activity."""
        today = datetime.now().date()
        
        # Reset counters if new day
        if today > self.last_summary_date:
            self.signals_generated_today = 0
            self.near_misses_today = 0
            self.candles_analyzed_today = 0
            self.rsi_values_today = []
            self.volume_ratios_today = []
            self.last_summary_date = today
        
        # Only log if we have data
        if self.candles_analyzed_today == 0:
            return
        
        # Calculate statistics
        rsi_min = min(self.rsi_values_today) if self.rsi_values_today else 0
        rsi_max = max(self.rsi_values_today) if self.rsi_values_today else 0
        rsi_avg = sum(self.rsi_values_today) / len(self.rsi_values_today) if self.rsi_values_today else 0
        
        vol_avg = sum(self.volume_ratios_today) / len(self.volume_ratios_today) if self.volume_ratios_today else 0
        vol_max = max(self.volume_ratios_today) if self.volume_ratios_today else 0
        
        logger.info("=" * 70)
        logger.info("=== DAILY SIGNAL SUMMARY ===")
        logger.info(f"Candles analyzed: {self.candles_analyzed_today}")
        logger.info(f"Signals generated: {self.signals_generated_today}")
        logger.info(f"Near misses: {self.near_misses_today}")
        logger.info(f"RSI range today: {rsi_min:.2f} - {rsi_max:.2f} (avg: {rsi_avg:.2f})")
        logger.info(f"  Long range: {self.rsi_long_min}-{self.rsi_long_max}")
        logger.info(f"  Short range: {self.rsi_short_min}-{self.rsi_short_max}")
        logger.info(f"Avg volume mult: {vol_avg:.2f}x (max: {vol_max:.2f}x, need: {self.volume_multiplier}x)")
        logger.info(f"Signal rate: {(self.signals_generated_today / self.candles_analyzed_today * 100):.2f}%")
        logger.info("=" * 70)
    
    def should_exit(self, position: Dict, current_price: float) -> Tuple[bool, Optional[str]]:
        """Check if position should be exited based on stop loss, take profit, or time."""
        signal_type = position.get('signal_type', 'LONG')
        entry_price = position.get('entry_price', 0)
        take_profit = position.get('take_profit', 0)
        stop_loss = position.get('stop_loss', 0)
        entry_time = position.get('entry_time')
        
        if signal_type == 'LONG':
            if current_price >= take_profit:
                return True, 'take_profit'
            if current_price <= stop_loss:
                return True, 'stop_loss'
        else:  # SHORT
            if current_price <= take_profit:
                return True, 'take_profit'
            if current_price >= stop_loss:
                return True, 'stop_loss'
        
        # Time-based exit
        if entry_time:
            from datetime import datetime, timedelta
            if isinstance(entry_time, str):
                entry_time = datetime.fromisoformat(entry_time)
            elapsed = datetime.now() - entry_time
            if elapsed > timedelta(minutes=self.config.POSITION_TIMEOUT_MINUTES):
                return True, 'timeout'
        
        return False, None
