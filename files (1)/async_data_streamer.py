import asyncio
import websockets
import json

async def stream_binance(symbol):
    uri = f"wss://stream.binance.com:9443/ws/{symbol.lower()}@trade"
    async with websockets.connect(uri) as ws:
        while True:
            msg = await ws.recv()
            tick = json.loads(msg)
            # Process tick data, publish to queue/db/handler...
            print(tick)

asyncio.run(stream_binance("btcusdt"))