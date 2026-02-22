"""RSI-only oversold/overbought strategy."""

import logging
from typing import Dict, List, Optional
import pandas as pd
from config import get_config

from .base import BaseStrategy, register_strategy

logger = logging.getLogger(__name__)


@register_strategy
class RSIOnlyStrategy(BaseStrategy):
    """Simple RSI oversold (long) / overbought (short) strategy."""

    id = "rsi_only"
    name = "RSI Only"
    description = "Buy on oversold (RSI < 30), sell on overbought (RSI > 70)."

    params_schema = {
        "rsi_period": {"type": "int", "default": 14, "min": 5, "max": 50},
        "rsi_oversold": {"type": "int", "default": 30, "min": 20, "max": 40},
        "rsi_overbought": {"type": "int", "default": 70, "min": 60, "max": 85},
    }

    def __init__(self, config=None):
        super().__init__(config)
        self.config = config or get_config()
        self.rsi_period = getattr(self.config, "RSI_PERIOD", 14)
        self.rsi_oversold = getattr(self.config, "RSI_OVERSOLD", 30)
        self.rsi_overbought = getattr(self.config, "RSI_OVERBOUGHT", 70)
        logger.info(
            f"RSIOnlyStrategy initialized: RSI({self.rsi_period}), "
            f"oversold<{self.rsi_oversold}, overbought>{self.rsi_overbought}"
        )

    def calculate_rsi(self, prices: List[float], period: int) -> List[float]:
        if len(prices) < period + 1:
            return []
        df = pd.Series(prices)
        delta = df.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.fillna(50).tolist()

    def calculate_indicators(self, candles: List[Dict]) -> Optional[Dict]:
        if len(candles) < self.rsi_period + 1:
            return None
        prices = [c["close"] for c in candles]
        rsi_values = self.calculate_rsi(prices, self.rsi_period)
        if not rsi_values:
            return None
        return {
            "price": prices[-1],
            "rsi": rsi_values[-1],
        }

    def generate_signal(self, candles: List[Dict], pair: str = "") -> Optional[Dict]:
        indicators = self.calculate_indicators(candles)
        if not indicators:
            return None

        price = indicators["price"]
        rsi = indicators["rsi"]
        take_profit_pct = getattr(self.config, "TAKE_PROFIT_MIN", 0.5) / 100
        stop_loss_pct = getattr(self.config, "STOP_LOSS_MIN", 0.25) / 100

        if rsi <= self.rsi_oversold:
            take_profit = price * (1 + take_profit_pct)
            stop_loss = price * (1 - stop_loss_pct)
            confidence = 50 + (self.rsi_oversold - rsi)  # Lower RSI = higher confidence
            confidence = min(95, max(60, confidence))
            return {
                "type": "LONG",
                "price": price,
                "confidence": confidence,
                "take_profit": take_profit,
                "stop_loss": stop_loss,
                "indicators": indicators,
            }
        if rsi >= self.rsi_overbought:
            take_profit = price * (1 - take_profit_pct)
            stop_loss = price * (1 + stop_loss_pct)
            confidence = 50 + (rsi - self.rsi_overbought)
            confidence = min(95, max(60, confidence))
            return {
                "type": "SHORT",
                "price": price,
                "confidence": confidence,
                "take_profit": take_profit,
                "stop_loss": stop_loss,
                "indicators": indicators,
            }
        return None
