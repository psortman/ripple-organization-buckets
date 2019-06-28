import re

import dslib.sql as sql
import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

from dash.dependencies import Input as I, Output as O, State as S

from app import app
import apps.nav.sidebar as sidebar
from apps.orgs.search.layout import layout as assign_layout
from apps.orgs.rename.layout import layout as rename_layout
# import apps.home

navbar = dbc.Navbar(
    children=[
        dbc.NavbarBrand(
            "Maestro",
            className="col-sm-3 col-md-2 mr-0"
        )
    ],
    dark=True,
    color='dark',
    className = "p-0 fixed-top flex-md-nowrap"
)

body = html.Div(
    children = [
        dbc.Row(
            children=[
                sidebar.layout,
                html.Div(
                    id="page-content", 
                    className="col-md-9 ml-sm-auto col-lg-10 px-4",
                    role="main"
                )
            ]
        )
    ],
    className="container-fluid"
)

app.layout = html.Div(
    children = [
        dcc.Location(id='url', refresh=False),
        navbar,
        body],
)



@app.callback(
    [
        O('page-content', 'children'),
        O("sidebar-org-assign-link", "className"),
        O("sidebar-org-rename-link", "className"),
    ],
    [I('url', 'pathname')]
)
def navigation(url):
    
    layout = None
    links = 2
    link_formatting = ["nav-link"] * links

    if url == '/orgs/assign':
        link_formatting[0] += " active"
        layout = assign_layout
    elif url == '/orgs/rename':
        link_formatting[1] += " active"
        layout = rename_layout

    return (
        layout,
    ) + tuple(link_formatting)


if __name__ == '__main__':
    app.run_server(debug=True, port=3001)