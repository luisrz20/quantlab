"""Concrete SQL adapters implementing domain ports."""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from quantlab.domain.entities.simulation import (
    EquityPointEntity, MetricsEntity, SimulationEntity, TradeEntity,
)
from quantlab.domain.ports.interfaces import IEquityRepo, IMetricsRepo, ISimulationRepo, ITradeRepo
from quantlab.infrastructure.db.mappers import (
    eq_to_e, eq_to_o, met_to_e, met_to_o, sim_to_e, sim_to_o, trade_to_e, trade_to_o,
)
from quantlab.infrastructure.db.orm_models import (
    EquityPointORM, MetricsORM, SimulationORM, TradeORM,
)


class SimRepo(ISimulationRepo):
    def __init__(self, s: AsyncSession) -> None:
        self._s = s

    async def create(self, e: SimulationEntity) -> SimulationEntity:
        o = sim_to_o(e)
        self._s.add(o)
        await self._s.flush()
        await self._s.refresh(o)
        return sim_to_e(o)

    async def get_by_id(self, sid: int) -> SimulationEntity | None:
        r = await self._s.execute(
            select(SimulationORM)
            .options(
                selectinload(SimulationORM.metrics),
                selectinload(SimulationORM.trades),
                selectinload(SimulationORM.equity_points),
            )
            .where(SimulationORM.id == sid)
        )
        o = r.scalar_one_or_none()
        return sim_to_e(o) if o else None

    async def list_all(self) -> list[SimulationEntity]:
        r = await self._s.execute(
            select(SimulationORM)
            .options(selectinload(SimulationORM.metrics))
            .order_by(SimulationORM.created_at.desc())
        )
        return [sim_to_e(x) for x in r.scalars().all()]

    async def update_status(self, sid: int, status: str, error: str | None = None) -> None:
        r = await self._s.execute(select(SimulationORM).where(SimulationORM.id == sid))
        o = r.scalar_one()
        o.status = status
        if error is not None:
            o.error_message = error
        await self._s.flush()


class TradeRepo(ITradeRepo):
    def __init__(self, s: AsyncSession) -> None:
        self._s = s

    async def bulk_insert(self, ts: list[TradeEntity]) -> None:
        self._s.add_all([trade_to_o(t) for t in ts])
        await self._s.flush()

    async def by_sim(self, sid: int) -> list[TradeEntity]:
        r = await self._s.execute(
            select(TradeORM).where(TradeORM.simulation_id == sid).order_by(TradeORM.timestamp)
        )
        return [trade_to_e(x) for x in r.scalars().all()]


class EquityRepo(IEquityRepo):
    def __init__(self, s: AsyncSession) -> None:
        self._s = s

    async def bulk_insert(self, pts: list[EquityPointEntity]) -> None:
        self._s.add_all([eq_to_o(p) for p in pts])
        await self._s.flush()

    async def by_sim(self, sid: int) -> list[EquityPointEntity]:
        r = await self._s.execute(
            select(EquityPointORM).where(EquityPointORM.simulation_id == sid).order_by(EquityPointORM.timestamp)
        )
        return [eq_to_e(x) for x in r.scalars().all()]


class MetricsRepo(IMetricsRepo):
    def __init__(self, s: AsyncSession) -> None:
        self._s = s

    async def upsert(self, m: MetricsEntity) -> None:
        r = await self._s.execute(select(MetricsORM).where(MetricsORM.simulation_id == m.simulation_id))
        o = r.scalar_one_or_none()
        if o:
            o.profit_pct, o.win_rate = m.profit_pct, m.win_rate
            o.max_drawdown, o.sharpe, o.num_trades = m.max_drawdown, m.sharpe, m.num_trades
        else:
            self._s.add(met_to_o(m))
        await self._s.flush()

    async def by_sim(self, sid: int) -> MetricsEntity | None:
        r = await self._s.execute(select(MetricsORM).where(MetricsORM.simulation_id == sid))
        o = r.scalar_one_or_none()
        return met_to_e(o) if o else None
