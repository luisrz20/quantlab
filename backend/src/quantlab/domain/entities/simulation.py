"""Domain entities — pure Python, zero framework imports."""
from __future__ import annotations

import enum
from dataclasses import dataclass
from datetime import datetime


class SimStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class SimulationEntity:
    ticker: str
    strategy_name: str
    config_json: dict
    status: SimStatus = SimStatus.PENDING
    error_message: str | None = None
    id: int | None = None
    created_at: datetime | None = None


@dataclass
class TradeEntity:
    simulation_id: int
    timestamp: str
    side: str
    qty: float
    price: float
    fees: float
    slippage: float
    pnl: float | None = None
    id: int | None = None


@dataclass
class EquityPointEntity:
    simulation_id: int
    timestamp: str
    equity: float
    id: int | None = None


@dataclass
class MetricsEntity:
    simulation_id: int
    profit_pct: float
    win_rate: float
    max_drawdown: float
    sharpe: float
    num_trades: int
    id: int | None = None
