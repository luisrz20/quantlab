"""Paper broker — simulated execution, pure domain logic."""
from __future__ import annotations

import logging
from dataclasses import dataclass, field

from quantlab.domain.strategies.engine import Action, Signal

log = logging.getLogger(__name__)


@dataclass
class ExecTrade:
    ticker: str
    side: str
    qty: float
    price: float
    fees: float
    slip_cost: float
    timestamp: str
    pnl: float | None = None


@dataclass
class EquitySnap:
    timestamp: str
    equity: float


@dataclass
class BrokerResult:
    initial_cash: float
    final_equity: float
    trades: list[ExecTrade] = field(default_factory=list)
    curve: list[EquitySnap] = field(default_factory=list)


class PaperBroker:
    """100%-cash market-order broker with slippage + commission."""

    def __init__(self, cash: float, commission: float, slippage: float) -> None:
        if cash <= 0:
            raise ValueError("cash must be > 0")
        if not (0 <= commission < 1):
            raise ValueError("commission_pct must be in [0, 1)")
        if not (0 <= slippage < 1):
            raise ValueError("slippage_pct must be in [0, 1)")
        self._init = cash
        self._cash = cash
        self._comm = commission
        self._slip = slippage
        self._pos: dict[str, float] = {}
        self._avg: dict[str, float] = {}
        self._trades: list[ExecTrade] = []
        self._curve: list[EquitySnap] = []

    def run(self, signals: list[Signal]) -> BrokerResult:
        if not signals:
            return BrokerResult(self._init, self._init, [], [EquitySnap("", self._init)])
        for s in signals:
            if s.action == Action.BUY:
                self._buy(s)
            elif s.action == Action.SELL:
                self._sell(s)
            self._snap(s)
        final = self._equity(signals[-1].price, signals[-1].ticker)
        return BrokerResult(self._init, final, self._trades, self._curve)

    def _buy(self, s: Signal) -> None:
        if self._cash <= 0 or self._pos.get(s.ticker, 0) > 0:
            return
        ep = s.price * (1 + self._slip)
        sc = s.price * self._slip
        qty = self._cash / ep
        fees = qty * ep * self._comm
        qty = (self._cash - fees) / ep
        if qty <= 0:
            return
        self._cash -= qty * ep + fees
        self._pos[s.ticker] = qty
        self._avg[s.ticker] = ep
        self._trades.append(ExecTrade(
            ticker=s.ticker, side="BUY", qty=qty, price=ep,
            fees=fees, slip_cost=sc * qty, timestamp=f"{s.date}T09:30:00",
        ))

    def _sell(self, s: Signal) -> None:
        qty = self._pos.get(s.ticker, 0.0)
        if qty <= 0:
            return
        ep = s.price * (1 - self._slip)
        sc = s.price * self._slip
        gross = qty * ep
        fees = gross * self._comm
        net = gross - fees
        cost = self._avg.get(s.ticker, ep) * qty
        pnl = round(net - cost, 4)
        self._cash += net
        del self._pos[s.ticker]
        del self._avg[s.ticker]
        self._trades.append(ExecTrade(
            ticker=s.ticker, side="SELL", qty=qty, price=ep,
            fees=fees, slip_cost=sc * qty,
            timestamp=f"{s.date}T16:00:00", pnl=pnl,
        ))

    def _equity(self, px: float, ticker: str) -> float:
        return self._cash + self._pos.get(ticker, 0.0) * px

    def _snap(self, s: Signal) -> None:
        self._curve.append(EquitySnap(
            f"{s.date}T16:00:00",
            round(self._equity(s.price, s.ticker), 2),
        ))
