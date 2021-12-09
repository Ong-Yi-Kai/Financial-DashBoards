import datetime as dt

import yfinance as yf

from dash import Dash
from dash import dcc, html
from dash.dependencies import Output, Input
import dash_bootstrap_components as dbc

from utils import *

all_intervals = ['1m', '2m', '5m', '15m', '30m', '60m',
                 '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo']

app = Dash(__name__, external_stylesheets=[dbc.themes.SUPERHERO],
                  meta_tags=[{'name': 'viewport',
                              'content': 'width=device-width, initial-scale=1.0'}]
                  )

server = app.server

app.layout = dbc.Container([
    # create row for selection of stocks
    dbc.Row([
        # select stock
        dbc.Col([dcc.Input(id='Stock down', type="text", value='MS', placeholder="Enter Ticker")])]),
    dbc.Row([dbc.Col([dcc.DatePickerRange(id='Date Picker',
                                          max_date_allowed=dt.datetime.today(),
                                          initial_visible_month=dt.date(2021, 1, 1),
                                          start_date=dt.date(2021, 1, 1),
                                          end_date=dt.date(2021, 12, 1),
                                          style={'width': "40%"})])]),
    dbc.Row([dbc.Col([dcc.Dropdown(id='Time Interval',
                                   placeholder='Select Time interval',
                                   value='1d',
                                   options=[{'label': x, 'value': x} for x in all_intervals],
                                   multi=False,
                                   style={'width': '40%'})])]),

    # create row for header
    dbc.Row([
        dbc.Col([html.H1('Impulse System', className='text-center text-primary font-weight-bold')]
                )
    ]),

    # create row for Screens
    dbc.Row([
        # Trend Indicator
        dbc.Col([
            # Header
            html.H2('Impulse Chart', className='text-center text-primary'),
            # Slider for Short EMA,,
            html.P('Select short EMA window length '),
            dcc.Slider(id='Short EMA window', min=1, max=50, step=1, value=11,
                       tooltip={"placement": "bottom", "always_visible": True}),
            # Slider for Long EMA
            html.P('Select Long EMA window length '),
            dcc.Slider(id='Long EMA window', min=1, max=50, step=1, value=22,
                       tooltip={"placement": "bottom", "always_visible": True}),
            # Slider for MACD signal window
            html.P('Select MACD signal window length '),
            dcc.Slider(id='MACD signal window', min=1, max=50, step=1, value=9,
                       tooltip={"placement": "bottom", "always_visible": True}),
            # graph of OHLC
            dcc.Graph(id='Trend Fig', figure={})
        ], xs=12, sm=12, md=12, lg=6, xl=6),

        # Oscillators
        dbc.Col([
            # Header
            html.H2('Oscillator', className='text-center text-primary'),
            # Tabs to choose type of oscillator
            dbc.Tabs(id='Oscillator Tabs', active_tab='RSI tab', children=[
                dbc.Tab(label='RSI', tab_id='RSI tab', labelClassName="font-weight-bold",
                        tab_style={'size': '3', 'marginLeft': '1'}),
                dbc.Tab(label='Stochastic Oscillator', tab_id='Stoch tab', labelClassName="font-weight-bold",
                        tab_style={'size': '3', 'marginLeft': '1'})]),
            html.P('Select window length '),
            dcc.Slider(id='Oscill window', min=1, max=50, step=1, value=14,
                       tooltip={"placement": "bottom", "always_visible": True}),
            dcc.Graph(id='Oscill Fig', figure={}),
        ], xs=12, sm=12, md=12, lg=6, xl=6)
    ])
])


# callback to ohlc
@app.callback([Output('Trend Fig', 'figure'),
               Output('Oscill Fig', 'figure')],
              [Input('Stock down', 'value'),
               Input('Date Picker', 'start_date'),
               Input('Date Picker', 'end_date'),
               Input('Time Interval', 'value'),
               Input('Short EMA window', 'value'),
               Input('Long EMA window', 'value'),
               Input('MACD signal window', 'value'),
               Input('Oscillator Tabs', 'active_tab'),
               Input('Oscill window', 'value')
               ])
def update_layout(ticker, start, end, int, short_ema, long_ema, signal_len, oscil_type, oscil_len):
    df = yf.download(ticker, start, end, interval=int)
    impulse_plt = plot_impulse_data(df, short_ema, long_ema, signal_len)
    graph=None

    if oscil_type == 'RSI tab':
        graph = plot_rsi(df, oscil_len)

    elif oscil_type == 'Stoch tab':
        graph = plot_stochastic_oscill(df, oscil_len)

    return impulse_plt, graph


if __name__ == '__main__':
    app.run_server()


