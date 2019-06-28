import re
import pickle
import ast

import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc

import dslib.sql as sql


from app import app
import apps.orgs.search.results
import apps.orgs.search.state
import apps.orgs.search.bar
import apps.orgs.search.modal
from utils import load_state

import apps.orgs.search.callbacks

N_ROWS = 20


header = html.Div(
    className="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom fluid",
    children=[
        html.H1("Assign Strings to Buckets", className="h2"),
    ],
)

layout = html.Div(
    children=[
        # Not Displayed at load time:
        apps.orgs.search.state.layout,
        apps.orgs.search.modal.layout,
        # Rendered at load time:
        header,
        apps.orgs.search.bar.layout,
        apps.orgs.search.results.layout,
    ]
)

