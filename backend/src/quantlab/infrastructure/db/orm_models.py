"""SQLAlchemy ORM models — infrastructure only, domain never imports this."""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import BigInteger, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class SimulationORM(Base):
    __tablename__ = "simulations"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    ticker: Mapped[str] = mapped_column(String(20), nullable=False)
    strategy_name: Mapped[str] = mapped_column(String(50), nullable=False)
    config_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_now)
    trades: Mapped[list["TradeORM"]] = relationship("TradeORM", back_populates="simulation", cascade="all, delete-orphan")
    equity_points: Mapped[list["EquityPointORM"]] = relationship("EquityPointORM", back_populates="simulation", cascade="all, delete-orphan")
    metrics: Mapped["MetricsORM | None"] = relationship("MetricsORM", back_populates="simulation", uselist=False, cascade="all, delete-orphan")


class TradeORM(Base):
    __tablename__ = "trades"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    simulation_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("simulations.id", ondelete="CASCADE"), nullable=False, index=True)
    timestamp: Mapped[str] = mapped_column(String(26), nullable=False)
    side: Mapped[str] = mapped_column(String(4), nullable=False)
    qty: Mapped[float] = mapped_column(Float, nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    fees: Mapped[float] = mapped_column(Float, nullable=False)
    slippage: Mapped[float] = mapped_column(Float, nullable=False)
    pnl: Mapped[float | None] = mapped_column(Float, nullable=True)
    simulation: Mapped["SimulationORM"] = relationship("SimulationORM", back_populates="trades")


class EquityPointORM(Base):
    __tablename__ = "equity_points"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    simulation_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("simulations.id", ondelete="CASCADE"), nullable=False, index=True)
    timestamp: Mapped[str] = mapped_column(String(26), nullable=False)
    equity: Mapped[float] = mapped_column(Float, nullable=False)
    simulation: Mapped["SimulationORM"] = relationship("SimulationORM", back_populates="equity_points")


class MetricsORM(Base):
    __tablename__ = "metrics"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    simulation_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("simulations.id", ondelete="CASCADE"), nullable=False, unique=True)
    profit_pct: Mapped[float] = mapped_column(Float, nullable=False)
    win_rate: Mapped[float] = mapped_column(Float, nullable=False)
    max_drawdown: Mapped[float] = mapped_column(Float, nullable=False)
    sharpe: Mapped[float] = mapped_column(Float, nullable=False)
    num_trades: Mapped[int] = mapped_column(Integer, nullable=False)
    simulation: Mapped["SimulationORM"] = relationship("SimulationORM", back_populates="metrics")
