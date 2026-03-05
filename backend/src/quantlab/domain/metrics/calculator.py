"""Metrics — pure math, no I/O."""
from __future__ import annotations

import math

from quantlab.domain.broker.paper_broker import BrokerResult
from quantlab.domain.entities.simulation import MetricsEntity


def compute(r: BrokerResult, sid: int) -> MetricsEntity:
    profit = ((r.final_equity - r.initial_cash) / r.initial_cash) * 100.0
    sells = [t for t in r.trades if t.side == "SELL" and t.pnl is not None]
    n = len(sells)
    wins = sum(1 for t in sells if (t.pnl or 0.0) > 0)
    return MetricsEntity(
        simulation_id=sid,
        profit_pct=round(profit, 4),
        win_rate=round((wins / n * 100.0) if n else 0.0, 4),
        max_drawdown=round(_dd(r), 4),
        sharpe=round(_sharpe(r), 4),
        num_trades=n,
    )


def _dd(r: BrokerResult) -> float:
    vals = [p.equity for p in r.curve]
    if len(vals) < 2:
        return 0.0
    peak, dd = vals[0], 0.0
    for v in vals:
        peak = max(peak, v)
        if peak > 0:
            dd = max(dd, (peak - v) / peak * 100.0)
    return dd


def _sharpe(r: BrokerResult, rf: float = 0.0) -> float:
    vals = [p.equity for p in r.curve]
    if len(vals) < 2:
        return 0.0
    rets = [
        (vals[i] - vals[i - 1]) / vals[i - 1]
        for i in range(1, len(vals))
        if vals[i - 1] != 0
    ]
    if not rets:
        return 0.0
    mu = sum(rets) / len(rets)
    var = sum((x - mu) ** 2 for x in rets) / max(len(rets) - 1, 1)
    std = math.sqrt(var)
    return 0.0 if std == 0 else (mu - rf) / std * math.sqrt(252)
