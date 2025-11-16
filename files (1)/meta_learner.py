import pandas as pd

class MetaLearner:
    def __init__(self):
        # symbol: {'best_strategy': str, 'meta_stats': dict}
        self.symbol_meta = {}

    def update(self, symbol, strategy_name, stats):
        meta = self.symbol_meta.setdefault(symbol, {"strategies": {}, "best_strategy": None, "meta_stats": {}})
        meta['strategies'][strategy_name] = stats
        # Select best strategy based on win_rate or other meta-stat
        best = max(meta['strategies'], key=lambda k: meta['strategies'][k].get('win_rate', 0))
        meta['best_strategy'] = best
        meta['meta_stats'] = meta['strategies'][best]

    def get_best_strategy(self, symbol):
        meta = self.symbol_meta.get(symbol)
        if meta:
            return meta['best_strategy'], meta['meta_stats']
        return None, {}

    def get_all(self):
        return self.symbol_meta