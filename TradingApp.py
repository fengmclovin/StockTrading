import yfinance as yf
import pandas as pd
data = yf.download("SPY AAPL", period="1mo")

data.iloc[:, :]
