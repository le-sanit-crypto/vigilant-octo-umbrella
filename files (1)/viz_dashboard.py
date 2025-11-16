import streamlit as st
import pandas as pd
import plotly.express as px

def show_heatmap(trade_df):
    # Example: correlation heatmap for symbols
    pivot = trade_df.pivot_table(index='symbol', columns='result', values='qty', aggfunc='sum').fillna(0)
    fig = px.imshow(pivot, text_auto=True, color_continuous_scale='RdBu')
    st.plotly_chart(fig)

def show_equity_curve(df):
    df = df.sort_index()
    df['cum_profit'] = df['Close'].diff().fillna(0).cumsum()
    fig = px.line(df, x=df.index, y='cum_profit', title="Equity Curve")
    st.plotly_chart(fig)

def show_scatter(df, x_col='RSI', y_col='MACD'):
    fig = px.scatter(df, x=x_col, y=y_col, color='Close')
    st.plotly_chart(fig)