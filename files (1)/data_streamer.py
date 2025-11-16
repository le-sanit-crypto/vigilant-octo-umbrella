import websocket
import json
import pandas as pd
from threading import Thread, Event

class MarketDataStreamer:
    def __init__(self, symbol, api_key, provider='finnhub'):
        self.symbol = symbol
        self.api_key = api_key
        self.provider = provider
        self.ws = None
        self.data = []
        self.stop_event = Event()

    def on_message(self, ws, message):
        msg = json.loads(message)
        # Parse according to provider schema
        if 'data' in msg:
            for tick in msg['data']:
                self.data.append(tick)

    def on_error(self, ws, error):
        print("Websocket error:", error)

    def on_close(self, ws):
        print("Websocket closed")

    def stream(self):
        # For Finnhub example
        url = f"wss://ws.finnhub.io?token={self.api_key}"
        self.ws = websocket.WebSocketApp(
            url,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close
        )
        def run_ws():
            self.ws.run_forever()
        t = Thread(target=run_ws)
        t.start()
        self.ws.send(json.dumps({'type':'subscribe','symbol':self.symbol}))
        while not self.stop_event.is_set():
            pass
        self.ws.close()

    def get_data(self):
        return pd.DataFrame(self.data)

    def stop(self):
        self.stop_event.set()