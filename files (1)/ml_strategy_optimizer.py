import pandas as pd
import numpy as np
from sklearn.model_selection import ParameterGrid
from backtest import backtest_strategy
from signals import compute_rsi

def random_strategy(df):
    # For demo: returns random Buy/Hold/Sell
    choice = np.random.choice(['Buy', 'Hold', 'Sell'])
    return choice

class MLStrategyOptimizer:
    def __init__(self, param_grid=None):
        self.param_grid = param_grid or {'rsi_low':[15,25,30], 'rsi_high':[70,75,80], 'sma_period':[15,20,30]}
        self.top_strategies = []

    def strategy_func(self, df, params):
        rsi = compute_rsi(df["Close"], period=14)
        if rsi.iloc[-1] < params['rsi_low']:
            return 'Buy'
        elif rsi.iloc[-1] > params['rsi_high']:
            return 'Sell'
        else:
            return 'Hold'

    def optimize(self, df):
        best_score = -np.inf
        best_params = None
        best_log = []
        for params in ParameterGrid(self.param_grid):
            strat = lambda data: self.strategy_func(data, params)
            log, stats = backtest_strategy(df, strategy_func=strat)
            score = stats['profit'] + stats['win_rate'] * 1000
            if score > best_score:
                best_score, best_params, best_log = score, params, log
        self.top_strategies.append({'params': best_params, 'score': best_score, 'log': best_log})
        return best_params, best_score, best_log

    def predict(self, df):
        if not self.top_strategies:
            return random_strategy(df)
        params = self.top_strategies[-1]['params']
        return self.strategy_func(df, params)