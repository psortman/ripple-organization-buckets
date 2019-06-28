import re
import pickle
import ast
import time

import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input as I, Output as O, State as S
import dash_bootstrap_components as dbc

import dslib.sql as sql

from app import app

import apps.orgs.search.results as results
import apps.orgs.search.state as state
import apps.orgs.search.bar as bar
import apps.orgs.search.modal as modal
import apps.orgs.search.layout as layout

from utils import load_state, save_state

INVALID = "invalid"
EXISTS = "exists"
NEW = "new"

@app.callback(
    [
        O(state.search.id, "children"),
        O(results.id, "children")
    ],
    [
        I(bar.search_button.id, "n_clicks"),
        I(bar.raw_string_input.id, "n_submit"),
        I(bar.bucket_name_input.id, "n_submit"),
        I(bar.bucket_id_input.id, "n_submit"),
        I(state.database_update.id, "children")
    ],
    [
        S(state.search.id, "children"),
        S(bar.raw_string_input.id, "value"),
        S(bar.bucket_name_input.id, "value"),
        S(bar.bucket_id_input.id, "value"),
    ]
)
def update_state_search(
    n_clicks,
    raw_string_n_submits,
    bucket_name_n_submits,
    bucket_id_n_submits,
    database_updated,
    previous_state,
    raw_string,
    bucket_name,
    bucket_id):
    # print(f"Called Update State of Search Bar {raw_string}")
    previous_state = load_state(previous_state)

    # Determine Whether to Run Search:
    # We require one of n_clicks/n_submits to be not None
    # The callback is called once before anything is populated.
    # In this case, we just ignore it. Otherwise, we want to run search.

    run_search = True if n_clicks else \
        True if raw_string_n_submits else \
        True if bucket_name_n_submits else \
        True if bucket_id_n_submits else False


    # If we run the search, do it!
    if run_search:
        raw_string = None if raw_string == '' else raw_string
        bucket_name = None if bucket_name == '' else bucket_name
        bucket_id = None if bucket_id == '' else bucket_id

        if raw_string or bucket_name or bucket_id:
            data = sql.execute(f"""
                SELECT 
                    raw_string as "Raw String"
                    , coalesce(edits.bucket, original.bucket) as "Bucket Name"
                    , coalesce(edits.bucket_id, original.bucket_id) as "Bucket ID"
                    , original.bucket_id as "Original Bucket ID"
                    , original.has_new_bucket as "New Bucket"
                FROM staging.organization_buckets original
                LEFT JOIN reference.organization_buckets_edits edits USING(raw_string)
                WHERE original.raw_string <> '' AND original.bucket <> '' {
                    f" AND (original.raw_string ~* '{raw_string}' ) " if raw_string else ''
                }{
                    f" AND (original.bucket ~* '{bucket_name}' ) " if bucket_name else ''
                }
                {
                    f" AND (original.bucket_id ~* '{bucket_id}' ) " if bucket_id else ''
                }
                ORDER BY CASE WHEN original.has_new_bucket THEN 1 ELSE 0 END DESC, 3,2,1
                LIMIT {results.N_ROWS}
            """)
        else:
            data = None
    else:
        data = None

    # Write out the current search state.
    new_state = {
        "raw_string": raw_string,
        "bucket_name": bucket_name,
        "bucket_id": bucket_id,
        "run_search": run_search,
        "data": data
    }

    return (
        save_state(new_state),
        results.generate_results_table(new_state.get("data"))
    )

@app.callback(
    O(state.result_clicks.id, "children"),
    [
        I(f"update-button-{row}", "n_clicks") for row in range(results.N_ROWS)
    ],
    [
        S(state.result_clicks.id, "children")
    ]
)
def update_update_button_clicks(*args):

    clicks = args[:-1]
    previous_state = load_state(args[-1])

    button_clicked = -1

    # If previous state doesn't exist, then just look for a click:
    if not args[-1]:
        for i, click in enumerate(clicks):
            if click:
                button_clicked = i
                break
        
    # If previous state does exist, we need to find the click that increased.
    else:
        previous_clicks = previous_state.get("clicks")
        for i, n_click, last_n_click in zip(range(len(clicks)), clicks, previous_clicks):
            if n_click:
                if n_click > last_n_click:
                    button_clicked = i

    # Ensure we've got no "None" clicks to store:
    clicks = list(clicks)
    for i, click in enumerate(clicks):
        if not click:
            clicks[i] = 0

    # Save state:
    return save_state({
        "clicks": clicks,
        "button_clicked": button_clicked
    })

@app.callback(
    O(modal.id, "children"),
    [
        I(state.result_clicks.id, "children")
    ],
    [
        S(state.search.id, "children")
    ]
)
def update_modal(result_button_clicks, search_state):
    print("Updating Modal")
    result_state = load_state(result_button_clicks)
    search_state = load_state(search_state)

    button_clicked = result_state.get("button_clicked")
    df = search_state.get("data")

    return modal.render_modal(button_clicked, df)

@app.callback(
    O(modal.id, "is_open"),
    [
        I(modal.id, "children"),
        I(modal.close_button.id, "n_clicks"),
        I(state.database_update.id, "children")
    ],
    [
        S(modal.id, "is_open"),
        S(state.result_clicks.id, "children")
    ]
)
def toggle_modal(result_clicks, close_n_clicks, database_update, previous_is_open, button_clicks):
    button_clicks = load_state(button_clicks)
    button_clicked = button_clicks.get("button_clicked", -1)
    print(f"Toggling Modal to {not previous_is_open}")


    if close_n_clicks is not None or (button_clicked >= 0):
        return not previous_is_open
    return previous_is_open

@app.callback(
    O(state.modal_validity.id, "children"),
    [
        I(modal.new_bucket_id.id, "n_submit"),
        I(modal.validate_button.id, "n_clicks"),
        I(modal.id, "is_open"),
    ],
    [
        S(modal.new_bucket_id.id, "value"),
    ]
)
def update_validity(bucket_id_submits, validate_clicks, is_open, bucket_id):
    bucket_name = None

    if bucket_id is None:
        validity = INVALID

    elif len(bucket_id) < 3:
        validity = INVALID

    elif not is_open:
        validity = INVALID
        bucket_id = None

    else:
        print("Checking if exists via database.")
        exists = sql.execute(f"SELECT bucket FROM staging.organization_buckets WHERE bucket_id = '{bucket_id}' LIMIT 1;")

        if exists.shape[0] > 0:
            validity = EXISTS
            bucket_name = exists['bucket'][0]

        else:
            validity = NEW

    return save_state({
        "validity": validity,
        "bucket_name": bucket_name,
        "bucket_id": bucket_id
    })

@app.callback(
    [
        O(modal.update_button.id, "disabled"),
        O(modal.update_button.id, "className"),
        O(modal.new_bucket_name.id, "value"),
        O(modal.new_bucket_name.id, "disabled"),
        O(modal.warning_form_text.id, "children"),
    ],
    [
        I(state.modal_validity.id, "children"),
    ]
)
def respond_to_validity(modal_validity):
    modal_validity = load_state(modal_validity)

    validity = modal_validity.get("validity", INVALID)
    
    disabled = False
    update_button_color = "btn-danger"
    new_bucket_name = modal_validity.get("bucket_name")
    new_bucket_name_disabled = True
    new_bucket_warning = ""


    if validity == INVALID:
        disabled = True
        update_button_color = "btn-danger"
    elif validity == NEW:
        update_button_color = "btn-warning"
        new_bucket_name_disabled = False
        new_bucket_warning = "Please choose a name for your new bucket."
    elif validity == EXISTS:
        update_button_color = "btn-success"

    return(
        disabled,
        update_button_color,
        new_bucket_name if new_bucket_name is not None else "",
        new_bucket_name_disabled,
        new_bucket_warning
    )

@app.callback(
    O(state.database_update.id, "children"),
    [
        I(modal.update_button.id, "n_clicks")
    ],
    [
        S(state.modal_validity.id, "children"),
        S(modal.new_bucket_id.id, "value"),
        S(modal.new_bucket_name.id, "value"),
        S(state.search.id, "children"),
        S(state.result_clicks.id, "children"),
    ]
)
def update_raw_string_bucket(update_clicks, modal_validity, bucket_id, bucket_name, search_results, result_clicks):
    modal_validity = load_state(modal_validity)
    validity = modal_validity.get('validity')

    data = load_state(search_results).get('data')
    button_clicked = load_state(result_clicks).get("button_clicked")

    if validity is None:
        return save_state({
                'updated':False
            })

    if validity == INVALID:
        return save_state({
                'updated':False
            })

    bucket_id = bucket_id if bucket_id is not None else ""
    bucket_name = bucket_name if bucket_name is not None else ""

    valid_bucket_id = modal_validity.get("bucket_id")
    valid_bucket_name = modal_validity.get("bucket_name")

    # It's okay if valid bucket name is none. Means it's a new bucket.
    if validity == NEW:
        if valid_bucket_id != bucket_id:
            return save_state({
                'updated':False
            })

    if validity == EXISTS:
        if valid_bucket_id != bucket_id or valid_bucket_name != valid_bucket_name:
            return save_state({
                'updated':False
            })

    raw_string = data["raw string"][button_clicked].replace("'", "\'")

    if sql.execute(f"SELECT count(*) FROM reference.organization_buckets_edits WHERE raw_string = '{raw_string}';")['count'][0] > 0:
        sql.execute(f"UPDATE reference.organization_buckets_edits SET bucket = '{bucket_name}' WHERE raw_string = '{raw_string}';")
        sql.execute(f"UPDATE reference.organization_buckets_edits SET bucket_id = '{bucket_id}' WHERE raw_string = '{raw_string}';")

    else:
        sql.execute(f"INSERT INTO reference.organization_buckets_edits (raw_string, bucket, bucket_id, time) VALUES ('{raw_string}', '{bucket_name}', '{bucket_id}', GETDATE());")

    print(f"Database updated: {raw_string} to {bucket_id} ({bucket_name})")
    return save_state({
            'updated':True
        })
    