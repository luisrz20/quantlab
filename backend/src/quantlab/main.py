"""FastAPI application factory with complete DI wiring."""
from __future__ import annotations

import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from quantlab.api.routes import simulations as sim_r
from quantlab.config import Settings, get_settings
from quantlab.infrastructure.data_providers.yfinance_provider import YFinanceProvider
from quantlab.infrastructure.db.orm_models import Base
from quantlab.infrastructure.db.session import build_engine, build_factory
from quantlab.infrastructure.repositories.sql_repos import EquityRepo, MetricsRepo, SimRepo, TradeRepo
from quantlab.services.simulation_service import SimulationService

log = logging.getLogger(__name__)


def _build_svc(session: AsyncSession, provider: YFinanceProvider) -> SimulationService:
    return SimulationService(
        sim_repo=SimRepo(session), trade_repo=TradeRepo(session),
        eq_repo=EquityRepo(session), met_repo=MetricsRepo(session),
        provider=provider,
    )


def create_app() -> FastAPI:
    cfg: Settings = get_settings()
    logging.basicConfig(level=getattr(logging, cfg.LOG_LEVEL.upper(), logging.INFO))

    app = FastAPI(title="QuantLab API", version="0.1.0", docs_url="/docs")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=cfg.ALLOWED_ORIGINS,
        allow_credentials=False,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Content-Type", "Accept"],
    )

    @app.middleware("http")
    async def sec_headers(req: Request, call_next):  # type: ignore[no-untyped-def]
        r = await call_next(req)
        r.headers["X-Content-Type-Options"] = "nosniff"
        r.headers["X-Frame-Options"] = "DENY"
        r.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return r

    @app.on_event("startup")
    async def startup() -> None:
        engine = build_engine(cfg)
        factory: async_sessionmaker[AsyncSession] = build_factory(engine)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        provider = YFinanceProvider()

        async def _dep():  # type: ignore[return]
            async with factory() as session:
                try:
                    yield _build_svc(session, provider)
                    await session.commit()
                except Exception:
                    await session.rollback()
                    raise

        app.dependency_overrides[sim_r.get_service] = _dep

    @app.get("/health", tags=["ops"])
    async def health() -> dict:
        return {"status": "ok"}

    @app.exception_handler(Exception)
    async def global_err(req: Request, exc: Exception) -> JSONResponse:
        log.exception("unhandled %s %s", req.method, req.url.path)
        return JSONResponse(500, {"detail": "Internal server error."})

    app.include_router(sim_r.router)
    return app


app = create_app()
