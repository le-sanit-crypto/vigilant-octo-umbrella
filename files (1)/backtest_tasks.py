from concurrent.futures import ProcessPoolExecutor
from apscheduler.schedulers.background import BackgroundScheduler
from backtest import backtest_strategy

def run_backtest(symbol, df, strategy_func):
    log, stats = backtest_strategy(df, strategy_func)
    # persist results, send event, etc
    return {"symbol": symbol, "log": log, "stats": stats}

def batch_backtest(symbols, dfs, strategy_func):
    with ProcessPoolExecutor() as executor:
        results = list(executor.map(
            lambda args: run_backtest(*args),
            [(sym, dfs[sym], strategy_func) for sym in symbols]
        ))
    return results

def schedule_periodic(func, interval_s):
    scheduler = BackgroundScheduler()
    scheduler.add_job(func, 'interval', seconds=interval_s)
    scheduler.start()
    return scheduler