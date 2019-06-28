import os
import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import pandas as pd
from dslib.sql.query import execute
import dash_bootstrap_components as dbc

external_stylesheets=[dbc.themes.COSMO]
# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.config['suppress_callback_exceptions']=True
app.config.supress_callback_exceptions = True
server = app.server
