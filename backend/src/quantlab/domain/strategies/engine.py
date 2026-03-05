"""Trading strategies — pure domain logic, deterministic, no I/O."""
from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any

import numpy as np
import pandas as pd

from quantlab.domain.ports.interfaces import MarketData

log = logging.getLogger(__name__)


class Action(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


@dataclass
class Signal:
    date: str
    action: Action
    price: float
    ticker: str


class Strategy(ABC):
    name: str = "base"

    def __init__(self, params: dict[str, Any]) -> None:
        self._check(params)
        self.params = params

    @abstractmethod
    def _check(self, p: dict[str, Any]) -> None: ...

    @abstractmethod
    def run(self, data: MarketData) -> list[Signal]: ...

    @classmethod
    def defaults(cls) -> dict[str, Any]:
        return {}

    def _force_close(self, closes: pd.Series, sigs: list[Signal], ticker: str) -> list[Signal]:
        buys = sum(1 for s in sigs if s.action == Action.BUY)
        sells = sum(1 for s in sigs if s.action == Action.SELL)
        if buys > sells and len(closes) > 0:
            sigs.append(Signal(
                date=str(closes.index[-1].date()),
                action=Action.SELL,
                price=float(closes.iloc[-1]),
                ticker=ticker,
            ))
        return sigs


class SMAStrategy(Strategy):
    """SMA crossover.  Params: fast (int, default 20), slow (int, default 50)."""

    name = "sma_crossover"

    def _check(self, p: dict[str, Any]) -> None:
        fast, slow = int(p.get("fast", 20)), int(p.get("slow", 50))
        if fast < 2:
            raise ValueError("fast must be >= 2")
        if slow <= fast:
            raise ValueError("slow must be > fast")

    @classmethod
    def defaults(cls) -> dict[str, Any]:
        return {"fast": 20, "slow": 50}

    def run(self, data: MarketData) -> list[Signal]:
        fast = int(self.params.get("fast", 20))
        slow = int(self.params.get("slow", 50))
        c = data.closes
        if len(c) < slow + 1:
            log.warning("SMA: not enough data (%d rows)", len(c))
            return []
        sf = c.rolling(fast).mean()
        ss = c.rolling(slow).mean()
        sigs: list[Signal] = []
        in_pos = False
        for i in range(slow, len(c)):
            pf, ps = float(sf.iloc[i - 1]), float(ss.iloc[i - 1])
            cf, cs = float(sf.iloc[i]), float(ss.iloc[i])
            dt, px = str(c.index[i].date()), float(c.iloc[i])
            if pf <= ps and cf > cs and not in_pos:
                sigs.append(Signal(dt, Action.BUY, px, data.ticker))
                in_pos = True
            elif pf >= ps and cf < cs and in_pos:
                sigs.append(Signal(dt, Action.SELL, px, data.ticker))
                in_pos = False
        return self._force_close(c, sigs, data.ticker)


class RSIStrategy(Strategy):
    """RSI mean reversion.  Params: period (14), lower (30), upper (70)."""

    name = "rsi_mean_reversion"

    def _check(self, p: dict[str, Any]) -> None:
        period = int(p.get("period", 14))
        lower, upper = float(p.get("lower", 30)), float(p.get("upper", 70))
        if period < 2:
            raise ValueError("period must be >= 2")
        if not (0 < lower < upper < 100):
            raise ValueError("Need: 0 < lower < upper < 100")

    @classmethod
    def defaults(cls) -> dict[str, Any]:
        return {"period": 14, "lower": 30, "upper": 70}

    @staticmethod
    def _rsi(c: pd.Series, n: int) -> pd.Series:
        d = c.diff()
        g = d.clip(lower=0).ewm(com=n - 1, min_periods=n).mean()
        lo = (-d.clip(upper=0)).ewm(com=n - 1, min_periods=n).mean()
        rs = g / lo.replace(0.0, np.nan)
        return 100.0 - (100.0 / (1.0 + rs))

    def run(self, data: MarketData) -> list[Signal]:
        period = int(self.params.get("period", 14))
        lower = float(self.params.get("lower", 30))
        upper = float(self.params.get("upper", 70))
        c = data.closes
        if len(c) < period + 2:
            return []
        rsi = self._rsi(c, period)
        sigs: list[Signal] = []
        in_pos = False
        for i in range(period, len(c)):
            v = float(rsi.iloc[i])
            if pd.isna(v):
                continue
            dt, px = str(c.index[i].date()), float(c.iloc[i])
            if v < lower and not in_pos:
                sigs.append(Signal(dt, Action.BUY, px, data.ticker))
                in_pos = True
            elif v > upper and in_pos:
                sigs.append(Signal(dt, Action.SELL, px, data.ticker))
                in_pos = False
        return self._force_close(c, sigs, data.ticker)


REGISTRY: dict[str, type[Strategy]] = {
    SMAStrategy.name: SMAStrategy,
    RSIStrategy.name: RSIStrategy,
}


def get_strategy(name: str, params: dict[str, Any]) -> Strategy:
    cls = REGISTRY.get(name)
    if cls is None:
        raise ValueError(f"Unknown strategy '{name}'. Available: {list(REGISTRY)}")
    return cls(params)
