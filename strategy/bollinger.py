"""Bollinger Bands strategy - trade at lower/upper band touches."""

import logging
from typing import Dict, List, Optional
import pandas as pd
from config import get_config

from .base import BaseStrategy, register_strategy

logger = logging.getLogger(__name__)


@register_strategy
class BollingerStrategy(BaseStrategy):
    """Buy at lower band, sell at upper band. Uses 20-period SMA and 2 std dev."""

    id = "bollinger"
    name = "Bollinger Bands"
    description = "Buy when price touches lower band, sell when price touches upper band."

    params_schema = {
        "period": {"type": "int", "default": 20, "min": 10, "max": 50},
        "std_dev": {"type": "float", "default": 2.0, "min": 1.0, "max": 3.0},
    }

    def __init__(self, config=None, **kwargs):
        super().__init__(config)
        self.config = config or get_config()
        self.period = 20
        self.std_dev = 2.0
        logger.info(
            f"BollingerStrategy initialized: period={self.period}, std_dev={self.std_dev}"
        )

    def calculate_indicators(self, candles: List[Dict]) -> Optional[Dict]:
        if len(candles) < self.period:
            return None
        prices = [c["close"] for c in candles]
        df = pd.Series(prices)
        sma = df.rolling(window=self.period).mean()
        std = df.rolling(window=self.period).std()
        upper = sma + (std * self.std_dev)
        lower = sma - (std * self.std_dev)

        price = prices[-1]
        sma_val = sma.iloc[-1]
        upper_val = upper.iloc[-1]
        lower_val = lower.iloc[-1]
        if pd.isna(sma_val) or pd.isna(upper_val) or pd.isna(lower_val):
            return None

        return {
            "price": price,
            "sma": float(sma_val),
            "upper": float(upper_val),
            "lower": float(lower_val),
        }

    def generate_signal(self, candles: List[Dict], pair: str = "") -> Optional[Dict]:
        indicators = self.calculate_indicators(candles)
        if not indicators:
            return None

        price = indicators["price"]
        lower = indicators["lower"]
        upper = indicators["upper"]
        # Band width as % of price
        band_pct = (upper - lower) / price if price > 0 else 0
        take_profit_pct = getattr(self.config, "TAKE_PROFIT_MIN", 0.5) / 100
        stop_loss_pct = getattr(self.config, "STOP_LOSS_MIN", 0.25) / 100

        # Long: price at or below lower band
        if price <= lower * 1.002:
            take_profit = price * (1 + take_profit_pct)
            stop_loss = price * (1 - stop_loss_pct)
            confidence = 60 + min(30, band_pct * 100)  # Wider bands = slightly more confidence
            return {
                "type": "LONG",
                "price": price,
                "confidence": min(90, confidence),
                "take_profit": take_profit,
                "stop_loss": stop_loss,
                "indicators": indicators,
            }
        # Short: price at or above upper band
        if price >= upper * 0.998:
            take_profit = price * (1 - take_profit_pct)
            stop_loss = price * (1 + stop_loss_pct)
            confidence = 60 + min(30, band_pct * 100)
            return {
                "type": "SHORT",
                "price": price,
                "confidence": min(90, confidence),
                "take_profit": take_profit,
                "stop_loss": stop_loss,
                "indicators": indicators,
            }
        return None
