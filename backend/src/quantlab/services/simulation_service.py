"""SimulationService — orchestrates the full pipeline."""
from __future__ import annotations

import logging

from quantlab.domain.broker.paper_broker import PaperBroker
from quantlab.domain.entities.simulation import (
    EquityPointEntity, MetricsEntity, SimulationEntity, SimStatus, TradeEntity,
)
from quantlab.domain.metrics.calculator import compute
from quantlab.domain.ports.interfaces import (
    IDataProvider, IEquityRepo, IMetricsRepo, ISimulationRepo, ITradeRepo,
)
from quantlab.domain.strategies.engine import REGISTRY, get_strategy

log = logging.getLogger(__name__)


class SimulationService:
    def __init__(
        self,
        sim_repo: ISimulationRepo,
        trade_repo: ITradeRepo,
        eq_repo: IEquityRepo,
        met_repo: IMetricsRepo,
        provider: IDataProvider,
    ) -> None:
        self._sim = sim_repo
        self._tr = trade_repo
        self._eq = eq_repo
        self._met = met_repo
        self._prov = provider

    async def run(
        self,
        ticker: str,
        strategy_name: str,
        strategy_params: dict,
        lookback_days: int,
        initial_cash: float,
        commission_pct: float,
        slippage_pct: float,
    ) -> int:
        if strategy_name not in REGISTRY:
            raise ValueError(f"Unknown strategy '{strategy_name}'")

        ent = await self._sim.create(SimulationEntity(
            ticker=ticker.upper().strip(),
            strategy_name=strategy_name,
            config_json=dict(
                ticker=ticker, strategy=strategy_name, params=strategy_params,
                lookback_days=lookback_days, initial_cash=initial_cash,
                commission_pct=commission_pct, slippage_pct=slippage_pct,
            ),
        ))
        sid = ent.id
        assert sid is not None
        await self._sim.update_status(sid, SimStatus.RUNNING.value)

        try:
            data = self._prov.get_prices(ent.ticker, lookback_days)
            p = {k: int(v) if isinstance(v, float) and v == int(v) else v for k, v in strategy_params.items()}
            sigs = get_strategy(strategy_name, p).run(data)
            result = PaperBroker(initial_cash, commission_pct, slippage_pct).run(sigs)
            metrics = compute(result, sid)

            await self._tr.bulk_insert([
                TradeEntity(
                    simulation_id=sid, timestamp=t.timestamp, side=t.side,
                    qty=t.qty, price=t.price, fees=t.fees, slippage=t.slip_cost, pnl=t.pnl,
                )
                for t in result.trades
            ])
            await self._eq.bulk_insert([
                EquityPointEntity(simulation_id=sid, timestamp=ep.timestamp, equity=ep.equity)
                for ep in result.curve
            ])
            await self._met.upsert(metrics)
            await self._sim.update_status(sid, SimStatus.COMPLETED.value)
            log.info("sim %d done — profit=%.2f%%", sid, metrics.profit_pct)

        except Exception as exc:
            log.exception("sim %d failed", sid)
            await self._sim.update_status(sid, SimStatus.FAILED.value, str(exc))
            raise

        return sid

    async def get_detail(self, sid: int) -> tuple[
        SimulationEntity, list[TradeEntity], list[EquityPointEntity], MetricsEntity | None,
    ]:
        sim = await self._sim.get_by_id(sid)
        if sim is None:
            raise ValueError(f"Simulation {sid} not found")
        return sim, await self._tr.by_sim(sid), await self._eq.by_sim(sid), await self._met.by_sim(sid)

    async def list_all(self) -> list[SimulationEntity]:
        return await self._sim.list_all()
