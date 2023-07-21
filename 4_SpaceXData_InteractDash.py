# Import required libraries
import pandas as pd
import numpy as np
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
spacex_df['label'] = np.where(spacex_df['class']==1,'Pass','Fail')
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # Dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(id='site-dropdown',
                                    options=[{'label': 'All Sites', 'value': 'ALL'},
                                        {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                                        {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
                                        {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'},
                                        {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'}],
                                    value='ALL',
                                    placeholder='Select a Launch Site here',
                                    searchable=True),
                                html.Br(),

                                # Add a pie chart to show the total successful launches count for all sites
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider',
                                    min=0, max=10000, step=1000,
                                    marks={0:'0',5000:'5000', 10000:'10000'},
                                    value=[min_payload,max_payload]),

                                # Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])


# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    filter_dt = spacex_df[spacex_df['Launch Site']==entered_site]
    if entered_site == 'ALL':
        fig = px.pie(spacex_df,values='class',names='Launch Site',title='Launch Success Rate')
    else:
        fig = px.pie(filter_dt,values=filter_dt['class'].value_counts().values,
        names=filter_dt['class'].value_counts().index,title='Launch Success Rate')
    return fig

# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
              [Input(component_id='site-dropdown', component_property='value'),
                Input(component_id="payload-slider", component_property="value")])
def get_scat_chart(entered_site,mass_range):
    filter_dt1 = spacex_df[(spacex_df['Payload Mass (kg)']>mass_range[0]) & (spacex_df['Payload Mass (kg)']<mass_range[1])]
    filter_dt2 = filter_dt1[filter_dt1['Launch Site']==entered_site]
    if entered_site == 'ALL':
        fig = px.scatter(filter_dt1,x='Payload Mass (kg)',y='class',color='Booster Version Category',title='Launch Success by Payload Mass (kg)')
    else:
        fig = px.scatter(filter_dt2,x='Payload Mass (kg)',y='class',color='Booster Version Category',title='Launch Success by Payload Mass (kg)')
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server()
