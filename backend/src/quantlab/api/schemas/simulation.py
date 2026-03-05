"""Pydantic v2 request/response schemas."""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, field_validator


class RunRequest(BaseModel):
    ticker: str = Field(..., min_length=1, max_length=20)
    strategy: str = Field(..., min_length=1, max_length=50)
    strategy_params: dict[str, Any] = Field(default_factory=dict)
    lookback_days: int = Field(default=180, ge=60, le=1825)
    initial_cash: float = Field(default=100_000.0, gt=0, le=10_000_000)
    commission_pct: float = Field(default=0.001, ge=0, lt=0.1)
    slippage_pct: float = Field(default=0.001, ge=0, lt=0.1)

    @field_validator("ticker")
    @classmethod
    def upper(cls, v: str) -> str:
        return v.upper().strip()


class MetricsOut(BaseModel):
    profit_pct: float
    win_rate: float
    max_drawdown: float
    sharpe: float
    num_trades: int


class TradeOut(BaseModel):
    id: int
    timestamp: str
    side: str
    qty: float
    price: float
    fees: float
    slippage: float
    pnl: float | None


class EquityOut(BaseModel):
    timestamp: str
    equity: float


class SimSummaryOut(BaseModel):
    id: int
    ticker: str
    strategy_name: str
    status: str
    created_at: str
    metrics: MetricsOut | None


class SimDetailOut(BaseModel):
    simulation: SimSummaryOut
    trades: list[TradeOut]
    equity_curve: list[EquityOut]


class RunResponse(BaseModel):
    simulation_id: int


class CompareOut(BaseModel):
    simulation_a: SimDetailOut
    simulation_b: SimDetailOut
