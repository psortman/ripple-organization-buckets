import re
import pickle
import ast

import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc

import dslib.sql as sql

search = html.Div(id="orgs-search-state-search",  style={'display': 'none'})
result_clicks = html.Div(id="orgs-search-state-result-clicks", style={'display': 'none'})
modal_validity = html.Div(id="orgs-search-state-modal-validity", style={'display': 'none'})
database_update = html.Div(id="orgs-search-state-database-update", style={'display': 'none'})

# State Information
layout = html.Div([
    search,
    result_clicks,
    modal_validity,
    database_update,
])