import os
import pandas as pd
import joblib
from concurrent.futures import ProcessPoolExecutor
from apscheduler.schedulers.background import BackgroundScheduler
import dask.dataframe as dd
from fastapi import FastAPI, WebSocket, Request
import redis
import psycopg2
from prometheus_client import start_http_server, Counter, Summary
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import requests
import logging

FINNHUB_KEY = "d4c40i1r01qoua32ddv0d4c40i1r01qoua32ddvg"
ALPACA_BASE = "https://paper-api.alpaca.markets/v2"
ALPACA_KEY = os.environ.get("ALPACA_KEY", "")
ALPACA_SECRET = os.environ.get("ALPACA_SECRET", "")

# ------- Monitoring --------
q_counter = Counter("tick_events_total", "Tick events received")
query_duration = Summary("query_duration_seconds", "Duration for queries")
start_http_server(9100)

# ------- Redis Pub/Sub --------
REDIS_HOST = "localhost"
redis_client = redis.Redis(host=REDIS_HOST)
pubsub = redis_client.pubsub()

# ------- FastAPI --------
app = FastAPI()

# ------- Tenacity Retry Decorator --------
def log_retry(retry_state):
    logging.warning(f"Retrying due to {retry_state.outcome.exception()} [attempt {retry_state.attempt_number}]")
def log_error(e):
    logging.error(f"Error: {e}")

@retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, max=10), retry=retry_if_exception_type(Exception), before_sleep=log_retry)
def resilient(callable_fn, *args, **kwargs):
    try:
        return callable_fn(*args, **kwargs)
    except Exception as e:
        log_error(e)
        raise

# ------- Finnhub Market Data --------
def get_finnhub_stock(symbol, start_ts, end_ts):
    url = f"https://finnhub.io/api/v1/stock/candle"
    params = {
        "symbol": symbol,
        "resolution": "D",
        "from": start_ts,
        "to": end_ts,
        "token": FINNHUB_KEY
    }
    r = requests.get(url, params=params)
    out = r.json()
    if out['s'] != 'ok':
        raise Exception('Finnhub no data')
    df = pd.DataFrame({
        "time": pd.to_datetime(out['t'], unit='s'),
        "open": out['o'],
        "high": out['h'],
        "low": out['l'],
        "close": out['c'],
        "volume": out['v'],
    }).set_index("time")
    return df

def get_finnhub_forex(pair, start_ts, end_ts):
    url = f"https://finnhub.io/api/v1/forex/candle"
    params = {
        "symbol": pair,
        "resolution": "D",
        "from": start_ts,
        "to": end_ts,
        "token": FINNHUB_KEY
    }
    r = requests.get(url, params=params)
    out = r.json()
    if out['s'] != 'ok':
        raise Exception('Finnhub no data')
    df = pd.DataFrame({
        "time": pd.to_datetime(out['t'], unit='s'),
        "open": out['o'],
        "high": out['h'],
        "low": out['l'],
        "close": out['c'],
        "volume": out['v'],
    }).set_index("time")
    return df

# ------- Finnhub News/Sentiment --------
def get_finnhub_news(symbol, count=5):
    url = f'https://finnhub.io/api/v1/news'
    params = {"symbol": symbol, "token": FINNHUB_KEY}
    r = requests.get(url, params=params)
    news = r.json()
    return news[:count] if isinstance(news, list) else []

# ------- Model Registry (joblib) --------
def get_model(symbol):
    try:
        return joblib.load(f"models/{symbol}_best.pkl")
    except Exception as e:
        logging.error(f"Model load error: {e}")
        return None

def save_model(symbol, model):
    joblib.dump(model, f"models/{symbol}_best.pkl")

# ------- TimescaleDB Integration --------
def store_tick(symbol, ts, price, volume):
    conn = psycopg2.connect(dbname='trading', user='user', password='pass', host='localhost')
    cur = conn.cursor()
    cur.execute("INSERT INTO ticks (symbol, ts, price, volume) VALUES (%s, %s, %s, %s)", (symbol, ts, price, volume))
    conn.commit()
    cur.close()
    conn.close()

# ------- Distributed ML (Dask) --------
def train_model(df, model_class, params, symbol):
    ddf = dd.from_pandas(df, npartitions=4)
    model = model_class(**params)
    model.fit(ddf.compute())
    save_model(symbol, model)
    return model

# ------- Multiprocessed Backtest + Scheduler --------
def run_backtest(symbol, df, strategy_func):
    log, stats = strategy_func(df)
    return {"symbol": symbol, "log": log, "stats": stats}

def batch_backtest(symbols, dfs, strategy_func):
    with ProcessPoolExecutor() as pool:
        results = pool.map(lambda args: run_backtest(*args), [(sym, dfs[sym], strategy_func) for sym in symbols])
    return list(results)

def start_scheduled_backtest(interval_s, symbols, dfs, strategy_func):
    scheduler = BackgroundScheduler()
    scheduler.add_job(lambda: batch_backtest(symbols, dfs, strategy_func), 'interval', seconds=interval_s)
    scheduler.start()
    return scheduler

# ------- Redis Event Broker --------
def publish_event(channel, data):
    redis_client.publish(channel, pd.io.json.dumps(data))

def subscribe_events(channel, handler):
    def listen():
        pubsub.subscribe(channel)
        for m in pubsub.listen():
            if m['type'] == 'message':
                handler(pd.read_json(m['data']))
    import threading; threading.Thread(target=listen, daemon=True).start()

# ------- Alpaca Broker API --------
def alpaca_order(side, symbol, qty):
    url = f"{ALPACA_BASE}/orders"
    headers = {
        "APCA-API-KEY-ID": ALPACA_KEY,
        "APCA-API-SECRET-KEY": ALPACA_SECRET
    }
    payload = {
        "symbol": symbol,
        "qty": qty,
        "side": side,
        "type": "market",
        "time_in_force": "gtc"
    }
    r = requests.post(url, json=payload, headers=headers)
    return r.json()

# ------- FastAPI Endpoints --------
@app.get("/signal/{symbol}")
@query_duration.time()
def get_signal(symbol: str):
    df = pd.read_csv(f"data/{symbol}_latest.csv")
    model = get_model(symbol)
    signal = model.predict(df.tail(1))[0]
    q_counter.inc()
    return {"signal": signal}

@app.websocket("/ws/ticks")
async def ticks_ws(websocket: WebSocket):
    await websocket.accept()
    while True:
        tick = resilient(redis_client.brpop, "ticks")
        await websocket.send_json(tick)

@app.post("/store_tick")
async def store_tick_api(req: Request):
    payload = await req.json()
    resilient(store_tick, payload['symbol'], payload['ts'], payload['price'], payload['volume'])
    return {"status": "ok"}

@app.post("/train_model")
async def train_model_api(req: Request):
    payload = await req.json()
    df = pd.DataFrame(payload['data'])
    model_class = payload.get("model_class")  # Should be passed as a class (from scikit-learn)
    params = payload.get("params", {})
    symbol = payload.get("symbol", "latest")
    resilient(train_model, df, model_class, params, symbol)
    return {"status": "trained"}

@app.post("/alpaca_order")
async def alpaca_order_api(req: Request):
    p = await req.json()
    resp = resilient(alpaca_order, p["side"], p["symbol"], p["qty"])
    return resp

@app.get("/finnhub_news/{symbol}")
def finnhub_news_api(symbol: str):
    news = resilient(get_finnhub_news, symbol)
    return {"news": news}

# ------- Entry point (Docker/K8s Ready) -------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)