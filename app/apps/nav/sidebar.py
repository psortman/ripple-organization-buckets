import re

import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc

import dslib.sql as sql

from app import app

organization_assign_link = dcc.Link("Assign", className="nav-link", href="/orgs/assign", id="sidebar-org-assign-link")
organization_rename_link = dcc.Link("Rename", className="nav-link", href="/orgs/rename", id="sidebar-org-rename-link")

layout = html.Nav(
    children=[
    html.Div(
        children=[
            html.H6(
                "Organizations",
                className="sidebar-heading d-flex justify-content-between align-items-center px-3 mt-4 mb-1 text-muted"
            ),
            html.Ul(
                children=[
                    html.Li(
                        className="nav-item",
                        children=organization_assign_link
                    ),
                    html.Li(
                        className="nav-item",
                        children=organization_rename_link
                    )
                ],
                className="nav flex-column"
            )
        ],
        className="sidebar-sticky"
    )
    ],
    className="col-md-2 d-none d-md d-md-block bg-light sidebar"
)