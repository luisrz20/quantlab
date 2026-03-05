"""Unit tests — pure domain, no DB, no yfinance network calls."""
from __future__ import annotations

import pandas as pd
import pytest

from quantlab.domain.broker.paper_broker import PaperBroker
from quantlab.domain.metrics.calculator import compute
from quantlab.domain.ports.interfaces import IDataProvider, MarketData
from quantlab.domain.strategies.engine import (
    Action, RSIStrategy, Signal, SMAStrategy, get_strategy,
)


def _data(prices: list[float], ticker: str = "T") -> MarketData:
    idx = pd.date_range("2020-01-01", periods=len(prices), freq="B")
    df = pd.DataFrame({
        "Open": prices, "High": [p * 1.01 for p in prices],
        "Low": [p * 0.99 for p in prices], "Close": prices,
        "Volume": [1_000_000] * len(prices),
    }, index=idx)
    return MarketData(ticker=ticker, df=df)


def _sigs(*specs: tuple[str, str, float]) -> list[Signal]:
    m = {"BUY": Action.BUY, "SELL": Action.SELL}
    return [Signal(d, m[s], p, "T") for d, s, p in specs]


class TestSMA:
    def test_defaults(self) -> None:
        assert SMAStrategy.defaults()["fast"] == 20

    def test_fast_gte_slow_raises(self) -> None:
        with pytest.raises(ValueError):
            SMAStrategy({"fast": 50, "slow": 20})

    def test_insufficient_data_returns_empty(self) -> None:
        assert SMAStrategy({"fast": 5, "slow": 10}).run(_data([100.0] * 8)) == []

    def test_produces_buy_and_sell(self) -> None:
        s = SMAStrategy({"fast": 3, "slow": 5})
        prices = [10] * 5 + [11, 12, 13, 14, 15, 14, 13, 11, 9, 8, 7, 7, 7, 7]
        sigs = s.run(_data(prices))
        assert any(x.action == Action.BUY for x in sigs)
        assert any(x.action == Action.SELL for x in sigs)


class TestRSI:
    def test_defaults(self) -> None:
        assert RSIStrategy.defaults()["period"] == 14

    def test_bad_thresholds(self) -> None:
        with pytest.raises(ValueError):
            RSIStrategy({"period": 14, "lower": 80, "upper": 30})

    def test_insufficient_data(self) -> None:
        assert RSIStrategy({"period": 14, "lower": 30, "upper": 70}).run(_data([100.0] * 10)) == []


class TestBroker:
    def test_no_signals(self) -> None:
        assert PaperBroker(10_000, 0, 0).run([]).final_equity == 10_000

    def test_profit_on_rising(self) -> None:
        r = PaperBroker(10_000, 0, 0).run(_sigs(("2022-01-01", "BUY", 100), ("2022-06-01", "SELL", 150)))
        assert r.final_equity > 10_000

    def test_loss_on_falling(self) -> None:
        r = PaperBroker(10_000, 0, 0).run(_sigs(("2022-01-01", "BUY", 100), ("2022-06-01", "SELL", 70)))
        assert r.final_equity < 10_000

    def test_invalid_cash_raises(self) -> None:
        with pytest.raises(ValueError):
            PaperBroker(-1, 0, 0)


class TestMetrics:
    def test_profit_positive_on_gain(self) -> None:
        r = PaperBroker(10_000, 0, 0).run(_sigs(("2022-01-01", "BUY", 100), ("2022-06-01", "SELL", 150)))
        m = compute(r, 1)
        assert m.profit_pct > 0
        assert m.win_rate == 100.0

    def test_drawdown_non_negative(self) -> None:
        r = PaperBroker(10_000, 0, 0).run(_sigs(("2022-01-01", "BUY", 100), ("2022-06-01", "SELL", 80)))
        m = compute(r, 1)
        assert m.max_drawdown >= 0

    def test_no_trades_zero_metrics(self) -> None:
        r = PaperBroker(10_000, 0, 0).run([])
        m = compute(r, 1)
        assert m.num_trades == 0
        assert m.win_rate == 0.0


class TestMockPipeline:
    def test_full_run(self) -> None:
        class MockProvider(IDataProvider):
            def get_prices(self, ticker: str, lookback_days: int) -> MarketData:
                return _data(list(range(50, 250)), ticker)

        data = MockProvider().get_prices("MOCK", 365)
        sigs = SMAStrategy({"fast": 5, "slow": 10}).run(data)
        result = PaperBroker(10_000, 0.001, 0.001).run(sigs)
        m = compute(result, 1)
        assert isinstance(m.profit_pct, float)
        assert m.num_trades >= 0


class TestRegistry:
    def test_get_sma(self) -> None:
        assert isinstance(get_strategy("sma_crossover", {"fast": 10, "slow": 30}), SMAStrategy)

    def test_get_rsi(self) -> None:
        assert isinstance(get_strategy("rsi_mean_reversion", {"period": 14, "lower": 30, "upper": 70}), RSIStrategy)

    def test_unknown_raises(self) -> None:
        with pytest.raises(ValueError):
            get_strategy("magic_strat", {})
