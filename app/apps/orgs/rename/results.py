import re
import pickle
import ast

import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input as I, Output as O, State as S
import dash_bootstrap_components as dbc

import dslib.sql as sql

N_ROWS=5

id = "orgs-rename-results"

state = html.Div(id="orgs-rename-results-state", style={"display": "none"})

def search(bucket_id, bucket_name):

    if bucket_id == '':
        bucket_id = None
    if bucket_name == '':
        bucket_name =  None

    if not bucket_id and not bucket_name:
        return None

    df = sql.execute(f"""
        SELECT
            coalesce(edits.bucket_id, original.bucket_id) as "Bucket ID"
            , coalesce(edits.bucket, original.bucket) as "Bucket Name"
            , LISTAGG(DISTINCT original.bucket_id, ', ') within group (order by original.bucket_id) as "Original Bucket ID"
            , count(*) as size
        FROM staging.organization_buckets original
        LEFT JOIN reference.organization_buckets_edits edits USING(raw_string)
        WHERE original.raw_string <> '' AND original.bucket <> '' {
            f" AND (original.bucket ~* '{bucket_name}' ) " if bucket_name else ''
        }
        {
            f" AND (original.bucket_id ~* '{bucket_id}' ) " if bucket_id else ''
        }
        GROUP BY 1,2
        ORDER BY 4 DESC,2,1,3
        LIMIT {N_ROWS}
    """)

    return df

def generate_result_table(df):

    # If no df passed, return None
    if df is None:
        return None
    table_header = [
        html.Thead(
            html.Tr(
                [
                    html.Th(col) for col in df.columns
                ] + [
                    html.Th(""),
                    html.Th(""),
                ]
            ),
            className='thead-dark'
        ),
    ]

    table_body = []
    for row in range(df.shape[0]):
        table_row = []
        for col in range(df.shape[1]):
            table_row.append(html.Td(str(df.iloc[row, col])))
        table_row.append(html.Td(dbc.Button("Rename", id=f"orgs-rename-results-rename-button-{row}", className='btn-sm', block=True)))
        table_row.append(html.Td(dbc.Button("Merge", id=f"orgs-rename-results-merge-button-{row}", className='btn-sm', block=True)))
        table_body.append(html.Tr(table_row))
    table_body = [html.Tbody(table_body)]

    # Add invisible buttons... the callback doesn't work unless all buttons exist. So we make them here and leave them invisible.
    for row in range(df.shape[0], N_ROWS):
        table_row = [html.Td(dbc.Button("Update", id=f"orgs-rename-results-rename-button-{row}", className='btn-sm'))]
        table_row.append(html.Td(dbc.Button("Update", id=f"orgs-rename-results-merge-button-{row}", className='btn-sm')))
        table_body.append(html.Tr(table_row, style={'display': 'none'}))


    return dbc.Table(
        table_header + table_body,
        bordered=True,
        hover=True,
        responsive=True,
        size='sm'
    )

layout = dcc.Loading(
    [
        html.Div(id=id),
        state
    ]
)