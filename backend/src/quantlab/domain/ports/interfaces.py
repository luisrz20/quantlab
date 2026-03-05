"""Domain ports — abstract interfaces for infrastructure adapters."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

import pandas as pd

from quantlab.domain.entities.simulation import (
    EquityPointEntity,
    MetricsEntity,
    SimulationEntity,
    TradeEntity,
)


@dataclass
class MarketData:
    """OHLCV value object."""

    ticker: str
    df: pd.DataFrame  # DatetimeIndex; cols: Open High Low Close Volume

    def __post_init__(self) -> None:
        required = {"Open", "High", "Low", "Close", "Volume"}
        missing = required - set(self.df.columns)
        if missing:
            raise ValueError(f"MarketData missing columns: {missing}")

    @property
    def closes(self) -> pd.Series:
        return self.df["Close"]

    def __len__(self) -> int:
        return len(self.df)


class IDataProvider(ABC):
    @abstractmethod
    def get_prices(self, ticker: str, lookback_days: int) -> MarketData: ...


class ISimulationRepo(ABC):
    @abstractmethod
    async def create(self, e: SimulationEntity) -> SimulationEntity: ...

    @abstractmethod
    async def get_by_id(self, sid: int) -> SimulationEntity | None: ...

    @abstractmethod
    async def list_all(self) -> list[SimulationEntity]: ...

    @abstractmethod
    async def update_status(self, sid: int, status: str, error: str | None = None) -> None: ...


class ITradeRepo(ABC):
    @abstractmethod
    async def bulk_insert(self, ts: list[TradeEntity]) -> None: ...

    @abstractmethod
    async def by_sim(self, sid: int) -> list[TradeEntity]: ...


class IEquityRepo(ABC):
    @abstractmethod
    async def bulk_insert(self, pts: list[EquityPointEntity]) -> None: ...

    @abstractmethod
    async def by_sim(self, sid: int) -> list[EquityPointEntity]: ...


class IMetricsRepo(ABC):
    @abstractmethod
    async def upsert(self, m: MetricsEntity) -> None: ...

    @abstractmethod
    async def by_sim(self, sid: int) -> MetricsEntity | None: ...
