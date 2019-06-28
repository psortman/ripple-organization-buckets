import re
import pickle
import ast

import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input as I, Output as O, State as S
import dash_bootstrap_components as dbc

import dslib.sql as sql

from app import app
from utils import load_state
import apps.orgs.rename.search_bar as search_bar
import apps.orgs.rename.results as results
import apps.orgs.rename.merge as merge

import apps.orgs.rename.callbacks

header = html.Div(
    className="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom fluid",
    children=[
        html.H1("Rename Organization Buckets", className="h2"),
    ],
)

layout = html.Div(
    children=[
        header,
        search_bar.layout,
        results.layout,
        merge.layout,
        # merge.state,
        # merge.database_update
    ]
)

