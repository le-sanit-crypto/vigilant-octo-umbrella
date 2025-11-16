from concurrent.futures import ProcessPoolExecutor
from backtest import backtest_strategy

def run_backtest(symbol, df, strategy_func):
    log, stats = backtest_strategy(df, strategy_func)
    return symbol, log, stats

def batch_backtest(symbols, dfs, strategy_func):
    with ProcessPoolExecutor() as pool:
        results = pool.map(
            lambda args: run_backtest(*args),
            [(symbol, dfs[symbol], strategy_func) for symbol in symbols]
        )
    return dict(results)