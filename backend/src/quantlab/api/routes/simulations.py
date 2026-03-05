"""API routes — thin controllers, zero business logic."""
from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, status

from quantlab.api.schemas.simulation import (
    CompareOut, EquityOut, MetricsOut, RunRequest, RunResponse,
    SimDetailOut, SimSummaryOut, TradeOut,
)
from quantlab.domain.entities.simulation import (
    EquityPointEntity, MetricsEntity, SimulationEntity, TradeEntity,
)
from quantlab.services.simulation_service import SimulationService

log = logging.getLogger(__name__)
router = APIRouter(prefix="/simulations", tags=["simulations"])


def get_service() -> SimulationService:
    raise NotImplementedError  # overridden in main.py


def _met(m: MetricsEntity | None) -> MetricsOut | None:
    if not m:
        return None
    return MetricsOut(profit_pct=m.profit_pct, win_rate=m.win_rate,
                      max_drawdown=m.max_drawdown, sharpe=m.sharpe, num_trades=m.num_trades)


def _sum(s: SimulationEntity, m: MetricsEntity | None = None) -> SimSummaryOut:
    return SimSummaryOut(
        id=s.id,  # type: ignore[arg-type]
        ticker=s.ticker, strategy_name=s.strategy_name, status=s.status.value,
        created_at=s.created_at.isoformat() if s.created_at else "",
        metrics=_met(m),
    )


def _det(
    s: SimulationEntity,
    ts: list[TradeEntity],
    eq: list[EquityPointEntity],
    m: MetricsEntity | None,
) -> SimDetailOut:
    return SimDetailOut(
        simulation=_sum(s, m),
        trades=[
            TradeOut(
                id=t.id,  # type: ignore[arg-type]
                timestamp=t.timestamp, side=t.side,
                qty=round(t.qty, 6), price=round(t.price, 4),
                fees=round(t.fees, 4), slippage=round(t.slippage, 4),
                pnl=round(t.pnl, 4) if t.pnl is not None else None,
            )
            for t in ts
        ],
        equity_curve=[EquityOut(timestamp=p.timestamp, equity=p.equity) for p in eq],
    )


@router.post("/run", response_model=RunResponse, status_code=status.HTTP_201_CREATED)
async def run(body: RunRequest, svc: SimulationService = Depends(get_service)) -> RunResponse:
    try:
        sid = await svc.run(
            ticker=body.ticker, strategy_name=body.strategy,
            strategy_params=body.strategy_params, lookback_days=body.lookback_days,
            initial_cash=body.initial_cash, commission_pct=body.commission_pct,
            slippage_pct=body.slippage_pct,
        )
        return RunResponse(simulation_id=sid)
    except ValueError as e:
        raise HTTPException(422, str(e))
    except Exception as e:
        log.exception("run failed")
        raise HTTPException(502, str(e))


@router.get("", response_model=list[SimSummaryOut])
async def list_sims(svc: SimulationService = Depends(get_service)) -> list[SimSummaryOut]:
    return [_sum(s) for s in await svc.list_all()]


@router.get("/compare/pair", response_model=CompareOut)
async def compare(a: int, b: int, svc: SimulationService = Depends(get_service)) -> CompareOut:
    try:
        sa, ta, ea, ma = await svc.get_detail(a)
        sb, tb, eb, mb = await svc.get_detail(b)
    except ValueError as e:
        raise HTTPException(404, str(e))
    return CompareOut(simulation_a=_det(sa, ta, ea, ma), simulation_b=_det(sb, tb, eb, mb))


@router.get("/{sim_id}", response_model=SimDetailOut)
async def get_sim(sim_id: int, svc: SimulationService = Depends(get_service)) -> SimDetailOut:
    try:
        s, ts, eq, m = await svc.get_detail(sim_id)
        return _det(s, ts, eq, m)
    except ValueError:
        raise HTTPException(404, "Not found")
