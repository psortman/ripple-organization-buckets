import re
import pickle
import ast

import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input as I, Output as O, State as S
import dash_bootstrap_components as dbc

import dslib.sql as sql

id = "orgs-rename-merge"

state = html.Div(id="orgs-rename-merge-state", style={"display": "none"})
database_update = html.Div(id="orgs-rename-merge-database-update", style={"display": "none"})
close_button = dbc.Button("Close", id="orgs-rename-merge-close-button", className="ml-auto")
merge_button = dbc.Button("Merge", id="orgs-rename-merge-merge-button", className="btn-danger", disabled=True)
new_bucket_id = dbc.Input(type="text", id="orgs-rename-merge-new-bucket-id", placeholder="New Bucket ID")


modal_footer = dbc.ModalFooter(children=[
    merge_button,
    close_button,
])

def render_modal(button_clicked, df):
    print(df)
    if df is None or button_clicked is None:
        bucket_id = "TEST"
    else:
        bucket_id = df['bucket id'][button_clicked]

    return [
        dbc.ModalHeader(f"Merge '{bucket_id}'"),
        dbc.ModalBody([
            dbc.Row([
                dbc.Col(
                    dbc.FormGroup([
                        dbc.Label("Old Bucket ID"),
                        dbc.Input(type="text", disabled=True, value=bucket_id)
                    ])
                ),
                dbc.Col(
                    dbc.FormGroup([
                        dbc.Label("Merge Into"),
                        new_bucket_id,
                        dbc.FormText("Press Enter to validate that this is a Bucket ID.")
                    ])
                )
            ])
        ]),
        modal_footer,
        state,
        database_update
    ]

def validate(bucket_id):
    if bucket_id is None:
        return False

    if bucket_id == '':
        return False
    
    return True if sql.execute(f"""
        SELECT 
        count(*)
    FROM staging.organization_buckets original
    LEFT JOIN reference.organization_buckets_edits edits USING(raw_string)
    WHERE coalesce(edits.bucket_id, original.bucket_id) = '{bucket_id.replace("'", "")}'
    """)['count'][0] > 0 else False

def merge(old_bucket_id, new_bucket_id):

    if old_bucket_id is None or new_bucket_id is None:
        return False

    new_bucket_name = sql.execute(f"""
    SELECT coalesce(edits.bucket, original.bucket) as bucket
    FROM staging.organization_buckets original
    LEFT JOIN reference.organization_buckets_edits edits USING(raw_string)
    WHERE coalesce(edits.bucket_id, original.bucket_id) = '{new_bucket_id}' LIMIT 1
    """).iloc[0, 0]

    sql.execute(f"""
    -- Insert any outstanding strings into the edits table.
        INSERT INTO reference.organization_buckets_edits
    (   SELECT original.raw_string, original.bucket, original.bucket_id, NULL, NULL, GETDATE()
        FROM staging.organization_buckets original
        LEFT JOIN reference.organization_buckets_edits edits USING(raw_string)
        WHERE edits.raw_string IS NULL AND original.bucket_id = '{old_bucket_id}'
    );
    COMMIT;
    -- Update the edits table:
    UPDATE reference.organization_buckets_edits SET time = GETDATE() WHERE bucket_id = '{old_bucket_id}';
    UPDATE reference.organization_buckets_edits SET bucket = '{new_bucket_name}' WHERE bucket_id = '{old_bucket_id}';
    UPDATE reference.organization_buckets_edits SET bucket_id = '{new_bucket_id}' WHERE bucket_id = '{old_bucket_id}';
    COMMIT;
    """)

    return True

layout = html.Div([
    dbc.Modal(
        children=render_modal(None, None),
        id=id,
        size="xl"),
])