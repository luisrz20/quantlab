"""Mappers — ORM ↔ domain entity conversion (anti-corruption layer)."""
from __future__ import annotations

from quantlab.domain.entities.simulation import (
    EquityPointEntity, MetricsEntity, SimulationEntity, SimStatus, TradeEntity,
)
from quantlab.infrastructure.db.orm_models import (
    EquityPointORM, MetricsORM, SimulationORM, TradeORM,
)


def sim_to_e(o: SimulationORM) -> SimulationEntity:
    return SimulationEntity(
        id=o.id, ticker=o.ticker, strategy_name=o.strategy_name,
        config_json=o.config_json, status=SimStatus(o.status),
        error_message=o.error_message, created_at=o.created_at,
    )


def sim_to_o(e: SimulationEntity) -> SimulationORM:
    return SimulationORM(
        ticker=e.ticker, strategy_name=e.strategy_name,
        config_json=e.config_json, status=e.status.value, error_message=e.error_message,
    )


def trade_to_o(e: TradeEntity) -> TradeORM:
    return TradeORM(
        simulation_id=e.simulation_id, timestamp=e.timestamp, side=e.side,
        qty=e.qty, price=e.price, fees=e.fees, slippage=e.slippage, pnl=e.pnl,
    )


def trade_to_e(o: TradeORM) -> TradeEntity:
    return TradeEntity(
        id=o.id, simulation_id=o.simulation_id, timestamp=o.timestamp,
        side=o.side, qty=o.qty, price=o.price, fees=o.fees, slippage=o.slippage, pnl=o.pnl,
    )


def eq_to_o(e: EquityPointEntity) -> EquityPointORM:
    return EquityPointORM(simulation_id=e.simulation_id, timestamp=e.timestamp, equity=e.equity)


def eq_to_e(o: EquityPointORM) -> EquityPointEntity:
    return EquityPointEntity(id=o.id, simulation_id=o.simulation_id, timestamp=o.timestamp, equity=o.equity)


def met_to_o(e: MetricsEntity) -> MetricsORM:
    return MetricsORM(
        simulation_id=e.simulation_id, profit_pct=e.profit_pct, win_rate=e.win_rate,
        max_drawdown=e.max_drawdown, sharpe=e.sharpe, num_trades=e.num_trades,
    )


def met_to_e(o: MetricsORM) -> MetricsEntity:
    return MetricsEntity(
        id=o.id, simulation_id=o.simulation_id, profit_pct=o.profit_pct,
        win_rate=o.win_rate, max_drawdown=o.max_drawdown, sharpe=o.sharpe, num_trades=o.num_trades,
    )
