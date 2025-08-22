# Services provided by the Yahoo Finance API via yfinance
from pandas import DataFrame
import yfinance as yf
from datetime import datetime
from ..app.schemas import IntervalEnum

# Lookup the current price of an asset using the asset symbol
def get_yahoo_price(symbol: str) -> tuple[float, datetime] | None:
    ticker: yf.Ticker = yf.Ticker(ticker=symbol)
    data: DataFrame = ticker.history(period="1d")
    if not data.empty:
        price = float(data["Close"].iloc[-1])
        price_time = data.index[-1].to_pydatetime()
        return price, price_time
    return None

# Lookup historical price data for an asset using the asset symbol
# optional to provide a start time, end time, and interval (IntervalEnum provides allowed values)
def get_yahoo_history(
    symbol: str, 
    start: datetime | None = None, 
    end: datetime | None = None, 
    interval: IntervalEnum | None = None
) -> DataFrame:
    ticker: yf.Ticker = yf.Ticker(ticker=symbol)
    return ticker.history(start=start, end=end, interval=interval)