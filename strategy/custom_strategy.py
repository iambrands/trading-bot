"""Custom strategy: runs a JSON strategy definition (Strategy Designer)."""

import logging
from typing import Any, Dict, List, Optional
import pandas as pd
from config import get_config

from .base import BaseStrategy, register_strategy

logger = logging.getLogger(__name__)


def _indicator_ema(candles: List[Dict], params: Dict) -> Optional[float]:
    period = int(params.get("period", 50))
    prices = [c["close"] for c in candles]
    if len(prices) < period:
        return None
    s = pd.Series(prices)
    ema = s.ewm(span=period, adjust=False).mean()
    return float(ema.iloc[-1])


def _indicator_rsi(candles: List[Dict], params: Dict) -> Optional[float]:
    period = int(params.get("period", 14))
    prices = [c["close"] for c in candles]
    if len(prices) < period + 1:
        return None
    df = pd.Series(prices)
    delta = df.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return float(rsi.fillna(50).iloc[-1])


def _indicator_volume_ratio(candles: List[Dict], params: Dict) -> Optional[float]:
    period = int(params.get("period", 20))
    volumes = [c.get("volume", 0) for c in candles]
    if len(volumes) < period:
        return 1.0
    avg = sum(volumes[-period:]) / period
    return (volumes[-1] / avg) if avg > 0 else 1.0


INDICATOR_REGISTRY = {
    "ema": _indicator_ema,
    "rsi": _indicator_rsi,
    "volume_ratio": _indicator_volume_ratio,
}


@register_strategy
class CustomStrategy(BaseStrategy):
    """Strategy that runs from a JSON definition (indicators + required/optional entry rules)."""

    id = "custom"
    name = "Custom (Designer)"
    description = "Run a strategy built in Strategy Designer (indicators + entry/exit rules)."

    params_schema = {}

    def __init__(self, config=None, definition: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.config = config or get_config()
        self.definition = definition or {}
        self._min_candles = 50
        if self.definition.get("indicators"):
            for ind in self.definition["indicators"]:
                p = ind.get("params") or {}
                period = p.get("period", 20)
                if isinstance(period, (int, float)):
                    self._min_candles = max(self._min_candles, int(period) + 1)

    def get_min_candles(self) -> int:
        return self._min_candles

    def calculate_indicators(self, candles: List[Dict]) -> Optional[Dict]:
        indicators = self.definition.get("indicators") or []
        out = {"price": candles[-1]["close"] if candles else 0}
        for ind in indicators:
            ind_id = ind.get("id")
            params = ind.get("params") or {}
            fn = INDICATOR_REGISTRY.get(ind_id) if ind_id else None
            if fn:
                val = fn(candles, params)
                if val is not None:
                    out[ind_id] = val
        return out if len(out) > 1 else None

    def _check_condition(self, cond_id: str, ind: Dict, side: str) -> bool:
        price = ind.get("price") or 0
        ema = ind.get("ema")
        rsi = ind.get("rsi")
        volume_ratio = ind.get("volume_ratio") or 1.0
        exit_cfg = self.definition.get("exit") or {}
        long_entry = self.definition.get("long_entry") or {}
        short_entry = self.definition.get("short_entry") or {}
        if cond_id == "price_above_ema":
            return ema is not None and price > ema
        if cond_id == "price_below_ema":
            return ema is not None and price < ema
        if cond_id == "rsi_in_range":
            if side == "long":
                lo = long_entry.get("rsi_min") or 45
                hi = long_entry.get("rsi_max") or 80
            else:
                lo = short_entry.get("rsi_min") or 20
                hi = short_entry.get("rsi_max") or 55
            return rsi is not None and lo <= rsi <= hi
        if cond_id == "rsi_oversold":
            return rsi is not None and rsi <= (exit_cfg.get("rsi_oversold") or 30)
        if cond_id == "rsi_overbought":
            return rsi is not None and rsi >= (exit_cfg.get("rsi_overbought") or 70)
        if cond_id == "volume_above_avg":
            mult = (long_entry if side == "long" else short_entry).get("volume_multiplier") or 0.9
            return volume_ratio >= mult
        return False

    def generate_signal(self, candles: List[Dict], pair: str = "") -> Optional[Dict]:
        ind = self.calculate_indicators(candles)
        if not ind:
            return None
        exit_cfg = self.definition.get("exit") or {}
        tp_pct = float(exit_cfg.get("take_profit_pct") or getattr(self.config, "TAKE_PROFIT_MIN", 1.5))
        sl_pct = float(exit_cfg.get("stop_loss_pct") or getattr(self.config, "STOP_LOSS_MIN", 0.5))
        price = ind["price"]
        for side, key in [("long", "long_entry"), ("short", "short_entry")]:
            entry_cfg = self.definition.get(key) or {}
            required = entry_cfg.get("required") or []
            optional = entry_cfg.get("optional") or []
            min_optional = int(entry_cfg.get("min_optional") or 0)
            req_ok = all(self._check_condition(c, ind, side) for c in required)
            opt_pass = sum(1 for c in optional if self._check_condition(c, ind, side))
            if not req_ok or opt_pass < min_optional:
                continue
            signal_type = "LONG" if side == "long" else "SHORT"
            if signal_type == "LONG":
                take_profit = price * (1 + tp_pct / 100)
                stop_loss = price * (1 - sl_pct / 100)
            else:
                take_profit = price * (1 - tp_pct / 100)
                stop_loss = price * (1 + sl_pct / 100)
            return {
                "type": signal_type,
                "price": price,
                "confidence": 70.0,
                "take_profit": take_profit,
                "stop_loss": stop_loss,
                "indicators": ind,
            }
        return None
