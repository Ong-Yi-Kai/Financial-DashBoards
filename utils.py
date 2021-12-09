import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots



def get_impulse_data(df,short_ema,long_ema,signal):
    raw = df.copy()
    # calculate 13-EMA and 26-EMA
    raw['short_EMA'] = raw['Adj Close'].ewm(span=short_ema, min_periods=short_ema).mean()
    raw['long_EMA'] = raw['Adj Close'].ewm(span=long_ema, min_periods=long_ema).mean()
    # calculate the 12,26,9-MACD-H
    raw['MACD'] = raw.short_EMA - raw.long_EMA
    raw['MACD_signal'] = raw.MACD.ewm(span=signal, min_periods=signal).mean()
    raw['MACD_H'] = raw.MACD - raw.MACD_signal
    return raw


def plot_impulse_data(data,short_ema,long_ema,signal):
    df = get_impulse_data(data,short_ema,long_ema,signal)
    # set impulse colors
    EMA_sign = np.sign(df.short_EMA.diff(1))
    MACD_H_sign = np.sign(df.MACD_H.diff(1))
    df['color'] = np.where((EMA_sign > 0) & (MACD_H_sign > 0), 1, np.nan)
    df['color'] = np.where((EMA_sign < 0) & (MACD_H_sign < 0), -1, df.color)
    df['color'].fillna(0, inplace=True)

    df_green = df[df.color == 1]
    df_red = df[df.color == -1]
    df_blue = df[df.color == 0]

    # create plot
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.3, 0.7],
                        subplot_titles=('MACD-H', 'OHLC'))
    colors = ['green', 'red', 'blue']
    # Green candlesticks
    fig.add_trace(
        go.Candlestick(x=df_green.index, open=df_green.Open, high=df_green.High, low=df_green.Low, close=df_green.Close,
                       opacity=0.7, name='OHLC', showlegend=False),
        row=2, col=1)
    # Red candlesticks
    fig.add_trace(go.Candlestick(x=df_red.index, open=df_red.Open, high=df_red.High, low=df_red.Low, close=df_red.Close,
                                 opacity=0.7, name='OHLC', showlegend=False),
                  row=2, col=1)
    # blue candlesticks
    fig.add_trace(
        go.Candlestick(x=df_blue.index, open=df_blue.Open, high=df_blue.High, low=df_blue.Low, close=df_blue.Close,
                       opacity=0.7, name='OHLC', showlegend=False),
        row=2, col=1)
    # fast EMA
    fig.add_trace(go.Scatter(x=df.index, y=df.short_EMA, line=go.scatter.Line(color='red'), name='short EMA', legendgroup=2),
                  row=2, col=1)
    # slow EMA
    fig.add_trace(
        go.Scatter(x=df.index, y=df.long_EMA, line=go.scatter.Line(color='black'), name='long EMA', legendgroup=2),
        row=2, col=1)
    # MACD-H plot
    fig.add_trace(
        go.Bar(x=df.index, y=df.MACD_H, name='MACD H', marker={'color': 'black'}, showlegend=False, legendgroup=1),
        row=1, col=1, )

    for i, color in enumerate(colors):
        fig.data[i].increasing.fillcolor = color
        fig.data[i].increasing.line.color = color
        fig.data[i].decreasing.fillcolor = color
        fig.data[i].decreasing.line.color = color

    fig.update_layout(paper_bgcolor='#ADD8E6')
    fig.update_layout(height=600,
                      legend=dict(
                          orientation="h",
                          yanchor="bottom",
                          y=0.55,
                          xanchor="right",
                          x=1))
    return fig


def plot_rsi(data,window_size):
    raw = data.copy()
    # calculate the postive and negative closings
    raw['pos_C'] = np.where(raw.Close.diff(1) > 0, raw.Close.diff(1), 0)
    raw['neg_C'] = np.where(raw.Close.diff(1) < 0, -1 * raw.Close.diff(1), 0)
    # sum those closing within the window
    raw['net_up'] = raw.pos_C.rolling(window=window_size, min_periods=window_size).sum()
    raw['net_down'] = raw.neg_C.rolling(window=window_size, min_periods=window_size).sum()
    # Calculate the RSI
    raw['RSI'] = (1 - 1 / (1 + (raw.net_up / raw.net_down))) * 100

    raw.drop(columns=['pos_C', 'neg_C', 'net_up', 'net_down'], axis=1, inplace=True)
    raw.dropna(how='any', axis=0, inplace=True)

    RSI = px.line(x=raw.index, y=raw.RSI, labels='RSI')
    RSI.add_hline(y=80, line_color='black', line_width=3, line_dash="dash",
                  annotation_text="overBOUGHT", )
    RSI.add_hline(y=20, line_color='black', line_width=3, line_dash="dash",
                  annotation_text='overSOLD', )
    RSI.update_layout(
         paper_bgcolor='#ADD8E6',
        height=400,
        annotations=[{'xanchor': 'left', 'x': 0, 'bgcolor': '#808282', 'opacity': 0.5, 'font': {'color': 'black'}},
                     {'xanchor': 'left', 'x': 0, 'bgcolor': '#808282', 'opacity': 0.5, 'font': {'color': 'black'}}]
    )

    return RSI

def plot_stochastic_oscill(data,n):
    raw=data.copy()
    #calculate the Highs and Lows of the privous n dat
    raw['L_n'] = raw.Low.shift(-1).rolling(window=n,min_periods=n).min()
    raw['H_n'] = raw.High.shift(-1).rolling(window=n,min_periods=n).max()
    #min max scale wrt L_n and H_n
    raw['C_L'] = raw.Close-raw.L_n
    raw['H_L'] = raw.H_n-raw.L_n
    raw['K'] = (raw.C_L/raw.H_L)*100
    raw['D'] = (raw.C_L.rolling(window=3,min_periods=3).sum()/raw.H_L.rolling(window=3,min_periods=3).sum())*100

    stoch = px.line(x=raw.index, y=[raw.K,raw.D], labels=['Fast Line','Slow Line'])
    stoch.add_hline(y=80, line_color='black', line_width=3, line_dash="dash",
                  annotation_text="overBOUGHT", )
    stoch.add_hline(y=20, line_color='black', line_width=3, line_dash="dash",
                  annotation_text='overSOLD', )
    stoch.update_layout(
       paper_bgcolor='#ADD8E6',
        height=400,
        annotations=[{'xanchor': 'left', 'x': 0, 'bgcolor': '#808282', 'opacity': 0.5, 'font': {'color': 'black'}},
                     {'xanchor': 'left', 'x': 0, 'bgcolor': '#808282', 'opacity': 0.5, 'font': {'color': 'black'}}],
        showlegend=False)
    return stoch
