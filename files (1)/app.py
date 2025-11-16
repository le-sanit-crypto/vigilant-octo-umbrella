import streamlit as st
import pandas as pd
import datetime

# === Modular imports ===
from portfolio import PortfolioManager
from signals import compute_rsi, compute_sma, compute_macd
from sentiment import news_with_sentiment
from backtest import backtest_strategy
from strategy import rule_builder_ui, evaluate_rules
from risk import risk_ui, risk_check
from historical_learning import HistoricalLearner
from strategy_adaptive import SymbolStrategies
from meta_learner import MetaLearner
from ml_strategy_optimizer import MLStrategyOptimizer
from ensemble import StrategyEnsemble
from data_streamer import MarketDataStreamer
from regime_detect import regime_detection, is_risk_on
from explainable_ai import explain_signal
from user_profiles import UserProfileManager
from broker_api import get_broker
from viz_dashboard import show_heatmap, show_equity_curve, show_scatter
from event_sentiment import news_with_sentiment, event_driven_signal
from scheduler import Scheduler
from notifications import notify_trade, notify_alert
from data_sources import get_source

st.set_page_config(layout="wide", page_title="Pro AI Trading Assistant Suite")

# == User profile and authentication ==
user_mgr = UserProfileManager()
username = st.sidebar.text_input("Username", value="default_user")
if not user_mgr.get_user(username):
    user_mgr.create_user(username)
user_profile = user_mgr.get_user(username)
st.sidebar.write(f"Risk tolerance: {user_profile['risk_tolerance']}")

st.sidebar.header("Provider & Broker Selection")
provider = st.sidebar.selectbox("Market Data Provider", ["yahoo", "binance"])
broker_type = st.sidebar.selectbox("Broker", ["Demo", "Alpaca", "Binance"])
api_credentials = st.secrets.get("api_credentials", {
    "alpaca_key": "YOUR_ALPACA_KEY",
    "alpaca_secret": "YOUR_ALPACA_SECRET",
    "binance_key": "YOUR_BINANCE_KEY",
    "binance_secret": "YOUR_BINANCE_SECRET"
})
broker_api = get_broker(broker_type, api_credentials)
data_source = get_source(provider)

portfolio_mgr = PortfolioManager()
strategy_mgr = SymbolStrategies()
meta_learner = MetaLearner()
learner = HistoricalLearner()
optimizer = MLStrategyOptimizer()
scheduler = Scheduler()

# === Main Navigation ===
tabs = st.tabs([
    "Trade", 
    "Strategy Builder",
    "Meta-Learning",
    "Market Stream (Live)", 
    "Ensemble", 
    "Regime Detection", 
    "Analytics",
    "Portfolio",
    "Event/Sentiment",
    "Scheduler", 
    "Broker",
    "Alerts",
    "Advanced"
])

# --- Asset selection ---
all_tickers = [
    'AAPL','MSFT','GOOGL','TSLA','AMZN',
    'BTCUSD','ETHUSD','SOLUSD','BNBUSD','XRPUSD',
    'EURUSD','USDJPY','GBPUSD','AUDUSD','USDCHF'
]
symbol = st.sidebar.selectbox("Choose asset symbol:", all_tickers, index=0)
start_date = st.sidebar.date_input("Start date", datetime.datetime.now() - datetime.timedelta(days=365))
end_date = st.sidebar.date_input("End date", datetime.datetime.now())
watchlist = st.sidebar.multiselect("Watchlist", all_tickers, default=[symbol], key="watchlist")
interval = st.sidebar.selectbox("Interval", ["1d", "1h", "5m"], index=0)

# Helper for fetching historical data with caching
@st.cache_data
def fetch_history_cached(symbol, start_date, end_date, provider, interval):
    source = get_source(provider)
    try:
        df = source.get_history(symbol, start_date, end_date, interval)
    except Exception as e:
        st.error(f"Data error for {symbol}: {e}")
        df = pd.DataFrame()
    return df

# === Trade Tab ===
with tabs[0]:
    st.header("Trade")
    df = fetch_history_cached(symbol, start_date, end_date, provider, interval)
    if not df.empty:
        df["RSI"] = compute_rsi(df["Close"])
        df["SMA_20"] = compute_sma(df["Close"])
        df["MACD"] = compute_macd(df["Close"])
        st.line_chart(df["Close"])
        st.dataframe(df.tail(15))
        qty = st.number_input("Order qty", min_value=1.0, value=1.0)
        last_price = df["Close"].iloc[-1]
        # Paper trade buttons
        if st.button("Simulate Buy"):
            portfolio_mgr.add_trade(username, {
                "symbol": symbol,
                "side": "buy", "entry": last_price, "exit": None,
                "qty": qty,
                "timestamp_entry": datetime.datetime.now(),
                "timestamp_exit": None, "result": None
            })
            notify_trade(symbol, "BUY", last_price)
        if st.button("Simulate Sell"):
            portfolio_mgr.add_trade(username, {
                "symbol": symbol,
                "side": "sell", "entry": last_price, "exit": last_price,
                "qty": qty,
                "timestamp_entry": datetime.datetime.now(),
                "timestamp_exit": datetime.datetime.now(), "result": "done"
            })
            notify_trade(symbol, "SELL", last_price)
        st.write("Trade Log:")
        trades_df = portfolio_mgr.get_trades(username, symbol)
        st.dataframe(trades_df)
    else:
        st.info("No historical data.")

# === Strategy Builder ===
with tabs[1]:
    st.header("Strategy Builder")
    rules = rule_builder_ui(existing_rules=st.session_state.get("rules", []))
    st.session_state["rules"] = rules
    if not df.empty:
        signal = evaluate_rules(df, rules)
        indicators = df.iloc[-1][["RSI", "SMA_20", "MACD"]].to_dict()
        st.write(f"Signal: {signal}")
        explanation = explain_signal(signal, indicators)
        st.write(f"Why? {explanation}")

# === Meta-Learning ===
with tabs[2]:
    st.header("Meta-Learning")
    if not df.empty and optimizer.top_strategies:
        for strat_name, params_info in [("MLStrategy", optimizer.top_strategies[-1]["params"])]:
            log, stats = backtest_strategy(df, strategy_func=lambda data: optimizer.strategy_func(data, params_info))
            meta_learner.update(symbol, strat_name, stats)
        best_strat, best_stats = meta_learner.get_best_strategy(symbol)
        st.write(f"Best Strategy for {symbol}: {best_strat}, Stats: {best_stats}")
        st.write(meta_learner.get_all())

# === Market Stream (Live) ===
with tabs[3]:
    st.header("Live Market Streaming")
    st.info("Demo only in browser: For full real streaming use websocket + DataStreamer module in server.")
    # streamer = MarketDataStreamer(symbol, api_key=api_credentials.get("finnhub"))
    # streamer.stream()

# === Ensemble Tab ===
with tabs[4]:
    st.header("Strategy Ensemble")
    if not df.empty and optimizer.top_strategies:
        strat_funcs = [lambda d: optimizer.strategy_func(d, optimizer.top_strategies[-1]["params"])]
        ensemble = StrategyEnsemble(strat_funcs)
        vote = ensemble.predict(df)
        st.write(f"Ensemble vote: {vote}")

# === Regime Detection Tab ===
with tabs[5]:
    st.header("Market Regime Detection")
    if not df.empty:
        df_reg = regime_detection(df)
        st.line_chart(df_reg["vol"])
        st.dataframe(df_reg[["regime"]].tail(20))
        st.success(f"Current regime: {is_risk_on(df_reg)}")

# === Analytics Tab ===
with tabs[6]:
    st.header("Analytics")
    if not df.empty:
        st.subheader("Equity Curve")
        show_equity_curve(df)
        st.subheader("RSI vs MACD Scatter")
        show_scatter(df, x_col="RSI", y_col="MACD")

# === Portfolio Tab ===
with tabs[7]:
    st.header("Portfolio Overview")
    st.dataframe(portfolio_mgr.get_portfolio(username))
    st.subheader("Portfolio Allocation")
    portfolio_df = portfolio_mgr.get_portfolio(username)
    if not portfolio_df.empty:
        st.pyplot(portfolio_df.groupby('symbol')['shares'].sum().plot.pie(autopct='%1.0f%%').figure)

# === Event/Sentiment Tab ===
with tabs[8]:
    st.header("Event & Sentiment Feed")
    news_df = news_with_sentiment(symbol)
    st.dataframe(news_df)
    st.write(f"Event-driven signal: {event_driven_signal(symbol)}")

# === Scheduler Tab ===
with tabs[9]:
    st.header("Automated Scheduling")
    interval_sec = st.number_input("Scheduler Interval (sec)", min_value=10, value=3600)
    def scheduled_backtest():
        if not df.empty:
            optimizer.optimize(df)
            meta_learner.update(symbol, "MLStrategy", {"interval":interval_sec})
            notify_alert(f"Backtest complete for {symbol}.")
    if st.button("Start Scheduler"):
        scheduler.schedule(f"Backtest_{symbol}", scheduled_backtest, interval_sec)
        st.success("Scheduled!")

# === Broker Tab ===
with tabs[10]:
    st.header("Broker Integration")
    if st.button("Connect to Broker"):
        ok = broker_api.connect()
        st.success(f"Connected to broker: {broker_type}" if ok else "Failed to connect.")
    st.write("Trade via Broker (demo):")
    broker_qty = st.number_input("Broker Qty", min_value=1.0, value=1.0)
    broker_price = st.number_input("Broker Price", min_value=0.0, value=1.0)
    if st.button("Broker Buy"):
        broker_api.buy(symbol, broker_qty, price=broker_price)
    if st.button("Broker Sell"):
        broker_api.sell(symbol, broker_qty, price=broker_price)

# === Alerts Tab ===
with tabs[11]:
    st.header("Web Alert Notifications")
    if st.button("Send Test Alert"):
        notify_alert("Test alert from the AI trading platform.")

# === Advanced Tab ===
with tabs[12]:
    st.header("Advanced Backend Features")
    st.info("This tab can be expanded with multiprocessing, async jobs, high-frequency trading simulation, or cluster-distributed ML training. Contact dev for further customization.")

st.sidebar.caption("AI Trading Assistant with modular data, brokers, strategies, analytics, and notifications.")