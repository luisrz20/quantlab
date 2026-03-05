"""yfinance adapter — concrete IDataProvider."""
from __future__ import annotations

import logging
from datetime import date, timedelta

import pandas as pd
import yfinance as yf

from quantlab.domain.ports.interfaces import IDataProvider, MarketData

log = logging.getLogger(__name__)


class YFinanceProvider(IDataProvider):
    def get_prices(self, ticker: str, lookback_days: int) -> MarketData:
        end = date.today()
        start = end - timedelta(days=lookback_days)
        log.info("yfinance: %s [%s → %s]", ticker, start, end)
        df: pd.DataFrame = yf.Ticker(ticker).history(
            start=start.isoformat(), end=end.isoformat(),
            auto_adjust=True, actions=False,
        )
        if df.empty:
            raise ValueError(f"No data for '{ticker}' ({lookback_days} days). Check symbol.")
        df = df[["Open", "High", "Low", "Close", "Volume"]].copy()
        df.index = pd.to_datetime(df.index).tz_localize(None)
        df.index.name = "Date"
        log.info("yfinance: %d rows for %s", len(df), ticker)
        return MarketData(ticker=ticker, df=df)
