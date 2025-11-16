import numpy as np

class StrategyEnsemble:
    def __init__(self, strategies):
        # strategies is a list of functions or ML models
        self.strategies = strategies

    def predict(self, df):
        votes = []
        for strat in self.strategies:
            try:
                votes.append(strat(df))
            except Exception:
                pass
        # Majority vote or weighted if available
        return max(set(votes), key = votes.count) if votes else 'Hold'

    def weighted_predict(self, df, weights=None):
        if not weights or len(weights)!=len(self.strategies):
            return self.predict(df)
        preds = [strat(df) for strat in self.strategies]
        choices = {'Buy':0, 'Sell':0, 'Hold':0}
        for p, w in zip(preds, weights):
            choices[p] += w
        return max(choices, key=choices.get)