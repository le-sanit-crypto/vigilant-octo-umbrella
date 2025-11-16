import requests

class AlpacaAPI:
    def __init__(self, credentials):
        self.key_id = credentials.get("alpaca_key")
        self.secret_key = credentials.get("alpaca_secret")
        self.base_url = "https://paper-api.alpaca.markets"

    def buy(self, symbol, qty):
        url = f"{self.base_url}/v2/orders"
        headers = {
            "APCA-API-KEY-ID": self.key_id,
            "APCA-API-SECRET-KEY": self.secret_key,
        }
        payload = {
            "symbol": symbol,
            "qty": qty,
            "side": "buy",
            "type": "market",
            "time_in_force": "gtc",
        }
        r = requests.post(url, json=payload, headers=headers)
        return r.json()

    def sell(self, symbol, qty):
        # Same as buy, but side="sell"
        # ... (similar implementation)
        pass

class BinanceAPI:
    def __init__(self, credentials):
        self.api_key = credentials.get("binance_key")
        self.secret = credentials.get("binance_secret")
        # ... implement REST calls or use ccxt ...

def get_broker(broker, credentials):
    if broker == "Alpaca":
        return AlpacaAPI(credentials)
    elif broker == "Binance":
        return BinanceAPI(credentials)
    # Add more as needed
    else:
        raise Exception("Unknown broker")