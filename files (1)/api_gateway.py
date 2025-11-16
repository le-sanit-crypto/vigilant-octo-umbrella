from fastapi import FastAPI, WebSocket, Request
import joblib
import pandas as pd

app = FastAPI()

@app.get("/signal/{symbol}")
def get_signal(symbol: str):
    df = pd.read_csv(f"data/{symbol}_latest.csv")
    model = joblib.load(f"models/{symbol}_best.pkl")
    signal = model.predict(df.tail(1))[0]
    return {"signal": signal}

@app.websocket("/ws/ticks")
async def ticks_ws(websocket: WebSocket):
    await websocket.accept()
    # Forward ticks from Redis or other broker
    while True:
        tick = await fetch_tick_somewhere()
        await websocket.send_json(tick)

# Add endpoints for dashboard analytics, event publishing, strategy submission!