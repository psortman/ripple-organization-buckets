import re
import pickle
import ast

import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input as I, Output as O, State as S
import dash_bootstrap_components as dbc

import dslib.sql as sql

bucket_name_input = dbc.Input(type="search", id="orgs-rename-bar-bucket-name-input", placeholder="Bucket Name")
bucket_id_input = dbc.Input(type="search", id="orgs-rename-bar-bucket-id-input", placeholder="Bucket ID")
search_button = dbc.Button("Search", id="orgs-rename-bar-search-button", color="primary", className="mr-1 btn search-button", block=True)


bucket_name_form = dbc.FormGroup(
    children=[
        dbc.Label("Bucket Name", html_for=bucket_name_input.id),
        bucket_name_input,
        dbc.FormText("Search through bucket names. Posix patterns work.", color="secondary")
    ]
)

bucket_id_form = dbc.FormGroup(
    children=[
        dbc.Label("Bucket ID", html_for=bucket_id_input.id),
        bucket_id_input,
        dbc.FormText("Search through the bucket IDs. Posix patterns work.", color="secondary")
    ]
)

search_button_div = html.Div(
    children=[
        search_button,
    ],
    className="search-botton-parent",
)

layout = dbc.Row(
    children=[
        dbc.Col(bucket_id_form),
        dbc.Col(bucket_name_form),
        dbc.Col(dbc.FormGroup(search_button_div), width=1, className="search-button-parent")
    ],
    className="form border-bottom"
)