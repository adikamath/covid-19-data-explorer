import dash, numpy as np
from datetime import datetime, timedelta
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd


####################################################################################################

def download_data(data_type):

    #store today's UTC date string to download the data from GitHub
    todays_datestring= datetime.utcnow().strftime("%m-%d-%Y")

    #yesterday's UTC date string
    yesterdays_datestring= (datetime.utcnow() - timedelta(days= 1)).strftime("%m-%d-%Y")


    if data_type == 'aggregated':

        try:
            #download data
            return pd.read_csv("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/{}.csv".format(todays_datestring))

        except:

            #download data
            return pd.read_csv("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/{}.csv".format(yesterdays_datestring))

    elif data_type == 'time_series':

        try:
            #download data
            t_data= pd.read_csv("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Confirmed.csv")

            #melt the dataset to unpivot date columns
            t_data= pd.melt(t_data, id_vars= t_data[['Province/State', 'Country/Region', 'Lat', 'Long']], value_vars= t_data.drop(labels= ['Province/State', 'Country/Region', 'Lat', 'Long'], axis= 1), var_name= 'Date', value_name= 'Confirmed Overall')

            #convert strings to date in the date column- we add a "20" string to each datestring so complete year
            t_data['Date']= t_data['Date'].apply(lambda x: datetime.strptime(x + "20", "%m/%d/%Y"))

            return t_data

        except:

            return 'Data Not Found'

data_timeseries= download_data('time_series')

data_countries_ts= data_timeseries.groupby(['Country/Region', 'Date'])['Confirmed Overall'].sum().reset_index()

ts_store1= []

for country in data_countries_ts['Country/Region'].unique():

    cache1= data_countries_ts[data_countries_ts['Country/Region'] == country]
    cache1['New Cases']= cache1['Confirmed Overall'] -  cache1['Confirmed Overall'].shift(1)

    ts_store1.append(cache1)

ts_data= pd.concat(ts_store1)


####################################################################################################

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

df = ts_data

available_countries = ts_data['Country/Region'].unique()

app.layout = html.Div([
    html.Div([

        html.Div([
            dcc.Dropdown(
                id='country_selection',
                options=[{'label': i, 'value': i} for i in available_countries],
                value= 'US'
            ),
            dcc.RadioItems(
                id='yaxis-type',
                options=[{'label': i, 'value': i} for i in ['Linear', 'Log']],
                value='Linear',
                labelStyle={'display': 'inline-block'}
            )
        ],
        style={'width': '48%', 'display': 'inline-block'})

            ]),

    dcc.Graph(id='indicator-graphic')
])

@app.callback(
                Output('indicator-graphic', 'figure'),
                [Input('country_selection', 'value'),
                 Input('yaxis-type', 'value')]
            )

def update_graph(country_value, yaxis_type):

    dff = df[df['Country/Region'] == country_value]

    return {
        'data': [dict(
            x= dff['Date'],
            y= dff['New Cases'],
            mode='lines+markers',
            marker={
                'size': 15,
                'opacity': 0.5,
                'line': {'width': 0.5, 'color': 'white'}
            }
        )],
        'layout': dict(
            yaxis={
                'title': 'New Cases',
                'type': 'linear' if yaxis_type == 'Linear' else 'log'
            },
            margin={'l': 60, 'b': 40, 't': 10, 'r': 0},
            hovermode='closest'
        )
    }


if __name__ == '__main__':
    app.run_server()
