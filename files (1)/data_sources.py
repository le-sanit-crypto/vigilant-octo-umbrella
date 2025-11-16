import pandas as pd
import requests

class YahooFinanceSource:
    def get_history(self, symbol, start, end, interval="1d"):
        url = f"https://query1.finance.yahoo.com/v7/finance/download/{symbol}?period1={int(pd.Timestamp(start).timestamp())}&period2={int(pd.Timestamp(end).timestamp())}&interval={interval}&events=history"
        df = pd.read_csv(url)
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.set_index('Date')
        return df

class BinanceSource:
    def get_history(self, symbol, interval="1h", limit=500):
        base, quote = symbol[:3], symbol[3:]
        url = f"https://api.binance.com/api/v3/klines?symbol={base}{quote}&interval={interval}&limit={limit}"
        r = requests.get(url)
        data = r.json()
        df = pd.DataFrame(data, columns=[
            'Open time','Open','High','Low','Close','Volume',
            'Close time','Quote Asset Volume','Number of Trades',
            'Taker Buy Base','Taker Buy Quote','Ignore'
        ])
        df['Open time'] = pd.to_datetime(df['Open time'], unit='ms')
        df = df.set_index('Open time')
        df['Close'] = df['Close'].astype(float)
        return df

# Add Alpaca, Polygon, Tiingo...
def get_source(provider):
    if provider == "yahoo":
        return YahooFinanceSource()
    elif provider == "binance":
        return BinanceSource()
    else:
        raise Exception("Unknown provider")