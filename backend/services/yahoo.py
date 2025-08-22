from pandas import DataFrame
import yfinance as yf

def get_yahoo_price(symbol: str) -> float | None:
    ticker: yf.Ticker = yf.Ticker(ticker=symbol)
    data: DataFrame = ticker.history(period="1d")
    if not data.empty:
        return float(data["Close"].iloc[-1])
    return None

def get_yahoo_history(symbol: str, period: str = "1y", interval: str = "1d") -> DataFrame:
    ticker: yf.Ticker = yf.Ticker(ticker=symbol)
    return ticker.history(period=period, interval=interval)