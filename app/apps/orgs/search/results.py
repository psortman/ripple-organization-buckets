import re
import pickle
import ast

import dash_table
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

import dslib.sql as sql

from app import app

N_ROWS=250

id = "orgs-search-results"

layout = dcc.Loading(
    html.Div(
        id=id
    )
)

def generate_results_table(df):

    # If no df passed, return None
    if df is None:
        return None

    table_header = [
        html.Thead(
            html.Tr(
                [
                    html.Th(col, style={'width': '22%'}) if col != 'new bucket' else html.Th(col, style={'width': '12%'}) for col in df.columns
                ] + [
                    html.Th('Actions', style={'width': '10%'})
                ]
            ),
            className='thead-dark'
        )
    ]

    table_body = []
    for row in range(df.shape[0]):
        table_row = []
        for col in range(df.shape[1]):
            if col < 4:
                table_row.append(html.Td(str(df.iloc[row, col]), id=f"update-row-{row}-col-{col}", className="col-2"))
            else:
                table_row.append(html.Td(str(df.iloc[row, col]), id=f"update-row-{row}-col-{col}"))
        # Add the update button
        table_row.append(html.Td(dbc.Button("Update", id=f"update-button-{row}", className='btn-sm', block=True)))
        table_body.append(html.Tr(table_row))
    table_body = [html.Tbody(table_body)]

    # Add invisible buttons... the callback doesn't work unless all buttons exist. So we make them here and leave them invisible.
    for row in range(df.shape[0], N_ROWS):
        table_row = [html.Td(dbc.Button("Update", id=f"update-button-{row}", className='btn-sm'))]
        table_body.append(html.Tr(table_row, style={'display': 'none'}))

    return dbc.Table(
        table_header + table_body,
        bordered=True,
        hover=True,
        responsive=True,
        size='sm'
    )