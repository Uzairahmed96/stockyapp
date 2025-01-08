import yfinance as yf
import pandas as pd
import numpy as np
import dash
from dash import Input, Output, html, dcc
from datetime import date
from dateutil.relativedelta import relativedelta
import plotly.express as px
import warnings
import dash_bootstrap_components as dbc

warnings.filterwarnings('ignore')

shared_label_style = {'font-size': '16px', 'text-align': 'center', 'margin-bottom': '8px'}
shared_component_style = {'width': '100%', 'height': '38px'}

# Define constants
interval = '1d'
tickers = ['AAPL', 'AMZN', 'GOOGL', 'MSFT', 'TSLA']

end = date.today()
start = date.today() - relativedelta(months=12)





# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])
server = app.server

app.layout = html.Div([



    dbc.Container([

    dbc.Row([

        dbc.Col([
            html.Div([
                html.H6('Select Tickers', style=shared_label_style),
                dcc.Dropdown(
                    id='ticker_list',
                    options=[{'label': 'Select', 'value': 'Select'}] + [{'label': value, 'value': value} for value in
                                                                        tickers],
                    clearable=False,
                    value='AAPL',
                    style=shared_component_style
                )
            ], style={'text-align': 'center'})
        ], width=2),

        dbc.Col([
            html.Div([
                html.H6('Select Date Range', style=shared_label_style),
                dcc.DatePickerRange(
                    id='date_range',
                    start_date=start,
                    end_date=end,
                    style=shared_component_style
                )
            ], style={'text-align': 'center'})
        ], width=3)
        ,

        dbc.Col([
            html.H3('Company', style={'text-align': 'center'}),
            dbc.Row([

                dbc.Col(html.Div(children='company', id='company_text', style={'fontSize': 20, 'text-align': 'center'})),
                dbc.Col(html.Div(children='website', id='website_text', style={'fontSize': 20, 'text-align': 'center'})),
                dbc.Col(html.Div(children='sector', id='sector_text', style={'fontSize': 20, 'text-align': 'center'}))


        ], className='info_border')
        ], width=7),
], style={'marginTop':25}),

    html.Br(),

    dbc.Row([

        dbc.Col([
            html.H5('Latest Stock Price', style={ 'text-align': 'center'}),
            html.Div(children='latest_price', id='price_text', style={'fontSize': 30, 'text-align': 'center'})
        ], width=3),
        dbc.Col([
            html.H5('% Change in Price', style={ 'text-align': 'center'}),
            html.Div(children='change_percent_price', id='change_percent_text',
                     style={'fontSize': 30, 'text-align': 'center'})
        ], width=3),
        dbc.Col([
            html.H5('Change in Price', style={ 'text-align': 'center'}),
            html.Div(children='change_price', id='change_text', style={'fontSize': 30, 'text-align': 'center'})
        ], width=3),
        dbc.Col([
            html.H5('Volatility', style={ 'text-align': 'center'}),
            html.Div(children='volatility', id='volatility_text', style={'fontSize': 30, 'text-align': 'center'})
        ], width=3)

    ], style={'margin':'20px', 'color': 'gradient(white, black)'}, className='card_container'),

        dbc.Row([
            dbc.Col(
                dcc.Graph(
                    id='price_overtime',
                    animate=False,
                    config={'displayModeBar': False},
                    figure=px.line().update_layout(
                                            plot_bgcolor='rgba(0, 0, 0, 0)',
                                            paper_bgcolor='rgba(0, 0, 0, 0)',
                                            xaxis={'autorange': True},  # Automatically adjust x-axis
                                            yaxis={'autorange': True}   # Automatically adjust y-axis
        ).update_xaxes(tickprefix='',
                          showgrid=False,
                          zeroline=False).update_yaxes(tickprefix='',
                          showgrid=False,
                          zeroline=False)

                ), width=12)
        ], className='card_container'),
        dbc.Row([
            dbc.Col(
                dcc.Graph(
                    id='change_overtime',
                    animate=False,
                    config={'displayModeBar': False},
                    figure=px.line().update_layout(
                                            plot_bgcolor='rgba(0, 0, 0, 0)',
                                            paper_bgcolor='rgba(0, 0, 0, 0)',
                                            xaxis={'autorange': True},  # Automatically adjust x-axis
                                            yaxis={'autorange': True}   # Automatically adjust y-axis
        ).update_xaxes(tickprefix='',
                          showgrid=False,
                          zeroline=False).update_yaxes(tickprefix='',
                          showgrid=False,
                          zeroline=False)),
                    width=12)
        ], className='card_container')

]),
    html.Br(),
    dbc.Row([
        dbc.Container([
            html.H3('Company Information'),
            dcc.Markdown(id='company_summary')
        ])
    ], className='company_information')

], style = {'margin': '25px', 'background':'linear-gradient(to bottom right, white, darkblue)'})

@app.callback(
    [
        Output(component_id='company_text', component_property='children'),
        Output(component_id='website_text', component_property='children'),
        Output(component_id='sector_text', component_property='children'),
        Output(component_id='price_text', component_property='children'),
        Output(component_id='change_text', component_property='children'),
        Output(component_id='change_percent_text', component_property='children'),
        Output(component_id='volatility_text', component_property='children'),
        Output(component_id='price_overtime', component_property='figure'),
        Output(component_id='change_overtime', component_property='figure'),
        Output(component_id='company_summary', component_property='children')
    ],
    [
        Input(component_id='ticker_list', component_property='value'),
        Input(component_id='date_range', component_property='start_date'),
        Input(component_id='date_range', component_property='end_date')
    ]
)
def update_graphs(value, start_date, end_date):

    data = yf.download(value, start=start_date, end=end_date, interval=interval)['Close']
    data = data.T.fillna(method='ffill').T

    change = pd.DataFrame(np.log(data/ data.shift(1))).reset_index()

    volatility_text = round(data.pct_change().std() * np.sqrt(252) * 100,2).astype(str)
    volatility_text = f'{volatility_text[0]}%'

    stock = yf.Ticker(value)
    company_summary = stock.info['longBusinessSummary']
    sector_text = stock.info['sector']
    website_text = stock.info['website']
    company_text = stock.info['longName']
    stock_info = stock.history(period="1d")

    if len(stock_info) > 0:
        # Get current price
        price_text = round(stock_info['Close'].iloc[0],2)  # Get the first row

        # Check if there is a previous close available
        previous_price = round(stock.info.get('previousClose', price_text),2)  # Use previous close if available

        # Calculate price change and percentage change
        change_text = round(price_text - previous_price, 2)
        change_percent_text = round((change_text / previous_price) * 100, 2) if previous_price != 0 else 0

        fig = px.line(data_frame=data,
                      x=data.index,
                      y=value,
                      color_discrete_sequence=['darkblue']).update_layout(
                                plot_bgcolor='rgba(0, 0, 0, 0)',
                                paper_bgcolor='rgba(0, 0, 0, 0)',
                                uirevision=True,
                                yaxis=dict(
                                    title=dict(
                                        text='Stock Price'))
        )
        fig.update_xaxes(tickprefix='',
                          showgrid=False,
                          zeroline=False)
        fig.update_yaxes(tickprefix='',
                          showgrid=False,
                          zeroline=False)


        fig1 = px.line(data_frame=change,
                       x=change['Date'],
                       y=change[value],
                       color_discrete_sequence=['darkblue','lightblue']).update_layout(
                                            plot_bgcolor='rgba(0, 0, 0, 0)',
                                            paper_bgcolor='rgba(0, 0, 0, 0)',
                                            uirevision=True,
                                            yaxis=dict(
                                                title=dict(
                                                    text='% Change'))
        )


        fig1.update_xaxes(tickprefix='',
                           showgrid=False,
                           zeroline=False,
                          color='white')
        fig1.update_yaxes(tickprefix='',
                          showgrid=False,
                          zeroline=True,
                          color='black')




        return  company_text, website_text, sector_text, price_text, change_text, change_percent_text, volatility_text,\
                fig, fig1, company_summary
    else:
        return 'No Data Available', '-', '-', '-', {}


if __name__ == "__main__":
    app.run_server(debug=False, port=8050)
