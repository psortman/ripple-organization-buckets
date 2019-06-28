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

import apps.orgs.rename.results as results
import apps.orgs.rename.search_bar as search_bar
import apps.orgs.rename.merge as merge

from utils import load_state, save_state

VALID = "valid"
INVALID = "invalid"

@app.callback(
    [
        O(results.state.id, "children"),
        O(results.id, "children")
    ],
    [
        I(search_bar.bucket_id_input.id, "n_submit"),
        I(search_bar.bucket_name_input.id, "n_submit"),
        I(search_bar.search_button.id, "n_clicks"),
        I(merge.database_update.id, "children")
    ],
    [
        S(search_bar.bucket_id_input.id, "value"),
        S(search_bar.bucket_name_input.id, "value"),
        S(results.state.id, "children")
    ]
)
def update_search_results(id_submits, name_submits, n_clicks, database_update, bucket_id, bucket_name, previous_search):

    previous_search = load_state(previous_search)
    database_update = load_state(database_update)

    # n_triggers = id_submits if id_submits else 0 
    #     + name_submits if name_submits else 0
    #     + n_clicks if n_clicks else 0

    # previous_triggers = previous_search.get("triggers", 0)

    # if n_triggers > previous_triggers or database_update.get("status"):
    search_results = results.search(bucket_id, bucket_name)

    state = save_state({
        'data': search_results,
        # 'n_triggers': n_triggers
    })

    layout = results.generate_result_table(search_results)

    return [
        state,
        layout
    ]

@app.callback(
    [
        O(merge.id, "children"),
        O(merge.state.id, "children")
    ],
    [
        I(f"orgs-rename-results-merge-button-{row}", "n_clicks") for row in range(results.N_ROWS)
    ],
    [
        S(results.state.id, "children"),
        S(merge.state.id, "children")
    ]
)
def merge_button_press(*args):
    results = load_state(args[-2])
    data = results.get("data")
    previous_clicks = load_state(args[-1]).get("clicks")
    clicks = list(args[:-2])

    button_clicked = None

    for i, click in enumerate(clicks):
        if click is None:
            clicks[i] = 0


    # if not previous_clicks:
    previous_clicks = [0] * len(clicks)

    for i, click, previous_click in zip(range(len(clicks)), clicks, previous_clicks):
        # print(f"{click} vs {previous_click}")
        if click > previous_click:
            button_clicked = i
            break

    state = {
        "clicks": clicks,
        "button_clicked": button_clicked,
        "bucket_id": data["bucket id"][button_clicked],
    }

    return [
        merge.render_modal(button_clicked, data),
        save_state(state)
    ]

@app.callback(
    O(merge.id, "is_open"),
    [
        I(merge.close_button.id, "n_clicks"),
        I(merge.state.id, "children"),
        I(merge.database_update.id, "children")
    ],
)
def toggle_merge_modal(n_clicks, merge_state, database_update):
    button_clicked = load_state(merge_state).get("button_clicked")
    database_update_status = load_state(database_update).get("status")

    if database_update_status:
        return False

    if n_clicks is None and button_clicked is not None:
        return True

    elif n_clicks is not None:
        return False

    return False

@app.callback(
    [
        O(merge.merge_button.id, "className"),
        O(merge.merge_button.id, "disabled")
    ],
    [
        I(merge.new_bucket_id.id, "n_submit"),
        I(merge.new_bucket_id.id, "n_blur")
    ],
    [
        S(merge.new_bucket_id.id, "value")
    ]
)
def validate_merge(n_submit, n_blur, new_bucket_id):

    print("Validating!", new_bucket_id)

    is_valid = merge.validate(new_bucket_id)
    
    if is_valid:
        return [
            "btn-success",
            False
        ]
    
    return [
        "btn-danger",
        True
    ]

@app.callback(
    O(merge.database_update.id, "children"),
    [
        I(merge.merge_button.id, "n_clicks")
    ],
    [
        S(merge.new_bucket_id.id, "value"),
        S(merge.state.id, "children")
    ]
)
def merge_bucket(n_clicks, new_bucket_id, merge_state):
    merge_state = load_state(merge_state)

    is_valid = merge.validate(new_bucket_id)
    status = False
    old_bucket_id = None
    if is_valid:
        old_bucket_id = merge_state.get("bucket_id")
        status = merge.merge(old_bucket_id, new_bucket_id)

    # print(status)
    return save_state({
        'status': status,
    })
    