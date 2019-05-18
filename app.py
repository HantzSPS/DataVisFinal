import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

df = pd.read_csv(
    'https://raw.githubusercontent.com/HantzSPS/Data-608-Visualization/master/master.csv')

available_indicators = df['generation'].unique()

app.layout = html.Div([
    html.Div([
        html.H1('Generational Suicide Rate by Country Over Time'),
        html.P('Suicide is a tragedy. According to estimates from the World Health Organisation (WHO), over 800,000 people die due to suicide every year.'
               'This corresponds to an age-standardized suicide rate of around 11.5 per 100,000 people'
               '– a figure equivalent to someone dying of suicide every 40 seconds.'),
        html.P('We are using kaggle dataset.  The file can be found here https://www.kaggle.com/russellyates88/suicide-rates-overview-1985-to-2016.'
                'Data suggest that the prevalence and characteristics of suicidal behavior vary widely between different communities and generation, in different demographic groups and over time.'
               'In this dashboard we want to appreciate the variation of suicide rate between country over time and between generation and the relationship with the gdp of the country.'),

        html.Div([
            dcc.Dropdown(
                id='crossfilter-xaxis-column',
                options=[{'label': i, 'value': i} for i in available_indicators],
                value='Millenials'
            ),
            dcc.RadioItems(
                id='crossfilter-xaxis-type',
                options=[{'label': i, 'value': i} for i in ['Linear', 'Log']],
                value='Linear',
                labelStyle={'display': 'inline-block'}
            )
        ],
        style={'width': '49%', 'display': 'inline-block'}),

        #html.Div([
            #dcc.Dropdown(
                #id='crossfilter-yaxis-column',
                #options=[{'label': i, 'value': i} for i in available_indicators],
                #value='Country'
            #),
            #dcc.RadioItems(
                #id='crossfilter-yaxis-type',
                #options=[{'label': i, 'value': i} for i in ['Linear', 'Log']],
                #value='Linear',
                #labelStyle={'display': 'inline-block'}
            #)        ], style={'width': '49%', 'float': 'right', 'display': 'inline-block'})
    ], style={
        'borderBottom': 'thin lightgrey solid',
        'backgroundColor': 'rgb(250, 250, 250)',
        'padding': '10px 5px'
    }),

    html.Div([
        dcc.Graph(
            id='crossfilter-indicator-scatter',
            hoverData={'points': [{'customdata': 'Japan'}]}
        )
    ], style={'width': '49%', 'display': 'inline-block', 'padding': '0 20'}),
    html.Div([
        dcc.Graph(id='x-time-series'),
        #dcc.Graph(id='y-time-series'),
    ], style={'display': 'inline-block', 'width': '49%', 'padding':'0 20 20 20'}),
    html.Div(dcc.Slider(
        id='crossfilter-year--slider',
        min=df['year'].min(),
        max=df['year'].max(),
        value=df['year'].max(),
        marks={str(year): str(year) for year in df['year'].unique()},
        
        ), style={'width': '100%', 'padding': '0px 20px 20px 20px'}),
    html.Div([
        html.H3('References'),
        html.P('https://ourworldindata.org/suicide'),
        html.P('https://www.codecrashcourse.com/deploy-your-web-app/'),
        html.P('https://dash.plot.ly/interactive-graphing'),

        ])
    ])


@app.callback(
    dash.dependencies.Output('crossfilter-indicator-scatter', 'figure'),
    [dash.dependencies.Input('crossfilter-xaxis-column', 'value'),
     #dash.dependencies.Input('crossfilter-yaxis-column', 'value'),
     dash.dependencies.Input('crossfilter-xaxis-type', 'value'),
     #dash.dependencies.Input('crossfilter-yaxis-type', 'value'),
     dash.dependencies.Input('crossfilter-year--slider', 'value')])
def update_graph(xaxis_column_name, #yaxis_column_name,
                 xaxis_type, #yaxis_type,
                 year_value):
    dff = df[df['year'] == year_value]

    return {
        'data': [go.Scatter(
            x=dff[dff['generation'] == xaxis_column_name]['suicides_no'],
            #y=dff[dff['generation'] == xaxis_column_name]['suicides_no'],
            text=dff[dff['generation'] == xaxis_column_name]['country'],
            customdata=dff[dff['generation'] == xaxis_column_name]['country'],
            mode='markers',
            marker={
                'size': 15,
                'opacity': 0.5,
                'line': {'width': 0.5, 'color': 'white'}
            }
        )],
        'layout': go.Layout(
            xaxis={
                'title': xaxis_column_name,
                'type': 'linear' if xaxis_type == 'Linear' else 'log'
            },
            #yaxis={
                #'title': yaxis_column_name,
                #'type': 'linear' if yaxis_type == 'Linear' else 'log'
            #},
            margin={'l': 40, 'b': 30, 't': 10, 'r': 0},
            height=450,
            hovermode='closest'
        )
        
    }


def create_time_series(dff, axis_type, title):
    return {
        'data': [go.Scatter(
            x=dff['year'],
            y=dff['gdp_per_capita ($)'],
            mode='lines+markers'
            #mode='lines'
        )],
        'layout': {
            'height': 450,
            'margin': {'l': 30, 'b': 30, 'r': 10, 't': 10},
            'annotations': [{
                'x': 0, 'y': 0.85, 'xanchor': 'left', 'yanchor': 'bottom',
                'xref': 'paper', 'yref': 'paper', 'showarrow': False,
                'align': 'left', 'bgcolor': 'rgba(255, 255, 255, 0.5)',
                'text': title
            }],
            'yaxis': {'type': 'linear' if axis_type == 'Linear' else 'log'},
            'xaxis': {'showgrid': False}
        }
    }


@app.callback(
    dash.dependencies.Output('x-time-series', 'figure'),
    [dash.dependencies.Input('crossfilter-indicator-scatter', 'hoverData'),
     dash.dependencies.Input('crossfilter-xaxis-column', 'value'),
     dash.dependencies.Input('crossfilter-xaxis-type', 'value')])
def update_y_timeseries(hoverData, xaxis_column_name, axis_type):
    country_name = hoverData['points'][0]['customdata']
    dff = df[df['country'] == country_name]
    dff = dff[dff['generation'] == xaxis_column_name]
    title = '<b>{}</b><br>{}'.format(country_name, xaxis_column_name)
    return create_time_series(dff, axis_type, title)


#@app.callback(
#    dash.dependencies.Output('y-time-series', 'figure'),
#    [dash.dependencies.Input('crossfilter-indicator-scatter', 'hoverData'),
#     dash.dependencies.Input('crossfilter-yaxis-column', 'value'),
#     dash.dependencies.Input('crossfilter-yaxis-type', 'value')])
#def update_x_timeseries(hoverData, yaxis_column_name, axis_type):
#    dff = df[df['country'] == hoverData['points'][0]['customdata']]
#    dff = dff[dff['generation'] == yaxis_column_name]
#    return create_time_series(dff, axis_type, yaxis_column_name)


if __name__ == '__main__':
    app.run_server(debug=True)
