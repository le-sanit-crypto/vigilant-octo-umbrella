import pandas as pd
import numpy as np
from sklearn.cluster import KMeans

def compute_volatility(prices, window=10):
    return prices.pct_change().rolling(window).std()

def regime_detection(df, n_regimes=2):
    df['vol'] = compute_volatility(df['Close'])
    # Cluster on volatility and/or returns
    X = df[['vol']].dropna().values
    kmeans = KMeans(n_clusters=n_regimes)
    regime_labels = kmeans.fit_predict(X)
    df['regime'] = np.nan
    df.loc[df[['vol']].dropna().index, 'regime'] = regime_labels
    return df

def is_risk_on(df):
    # Basic demo: if volatility is high, risk-off. Else, risk-on.
    vol = compute_volatility(df['Close']).iloc[-1]
    return 'risk-on' if vol < 0.02 else 'risk-off'