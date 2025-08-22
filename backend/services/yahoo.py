from pandas import DataFrame
import yfinance as yf
from datetime import datetime
from ..app.schemas import IntervalEnum

def get_yahoo_price(symbol: str) -> float | None:
    ticker: yf.Ticker = yf.Ticker(ticker=symbol)
    data: DataFrame = ticker.history(period="1d")
    if not data.empty:
        return float(data["Close"].iloc[-1])
    return None

def get_yahoo_history(
    symbol: str, 
    start: datetime | None = None, 
    end: datetime | None = None, 
    interval: IntervalEnum | None = None
) -> DataFrame:
    ticker: yf.Ticker = yf.Ticker(ticker=symbol)
    return ticker.history(start=start, end=end, interval=interval)