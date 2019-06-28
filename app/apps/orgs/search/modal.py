import re
import pickle
import ast

import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc

import dslib.sql as sql
import pandas as pd

id = "orgs-search-modal-layout"
close_button = dbc.Button("Close", id="orgs-search-modal-close-button", className="ml-auto")
update_button = dbc.Button("Update", id="orgs-search-modal-update-button", className="btn-danger", disabled=True)
validate_button = dbc.Button("Validate", id="orgs-search-modal-validate-button")
new_bucket_id = dbc.Input(type="text", id="orgs-modal-new-bucket-id", placeholder="New Bucket ID", autoFocus=True)
new_bucket_name = dbc.Input(type="text", id="orgs-search-modal-new-bucket-name", disabled=True)
warning_form_text = dbc.FormText(color="warning", id="orgs-search-modal-warning-form-text")

modal_footer = dbc.ModalFooter(children=[
    validate_button,
    update_button,
    close_button    
])

def render_modal(button_clicked, df):
    if df is None or button_clicked is None:
        return [new_bucket_id, new_bucket_name, warning_form_text, modal_footer]

    if button_clicked < 0:
        return [new_bucket_id, new_bucket_name, warning_form_text, modal_footer]

    return [
        dbc.ModalHeader(f"Update '{df['raw string'][button_clicked]}' Bucket"),
        dbc.ModalBody([
            dbc.Row([
                dbc.Col(
                    dbc.FormGroup([
                        dbc.Label("Old Bucket ID"),
                        dbc.Input(type="text", disabled=True, value=df['bucket id'][button_clicked])
                    ])
                ),
                dbc.Col(
                    dbc.FormGroup([
                        dbc.Label("Old Bucket Name"),
                        dbc.Input(type="text", disabled=True, value=df['bucket name'][button_clicked])
                    ])
                )
            ]),
            dbc.Row([
                dbc.Col(dbc.FormGroup(
                    children=[
                        dbc.Label("New Bucket ID"),
                        new_bucket_id,
                        dbc.FormText("Press Enter to check whether this is a valid or existing bucket ID.", color="secondary")
                    ]
                )),
                dbc.Col(dbc.FormGroup(
                    children=[
                        dbc.Label("New Bucket Name"),
                        new_bucket_name,
                        warning_form_text
                    ]
                ))
            ])
        ]),
        modal_footer
    ]


layout = dbc.Modal(
    children=render_modal(None, None),
    id=id,
    size="xl"
)