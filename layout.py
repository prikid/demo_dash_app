import dash_bootstrap_components as dbc
from dash import dcc, html


def layout():
    return html.Div([
        navbar(),
        dbc.Container([
            html.H1("Companies info", className="my-4"),

            html.Div([
                dbc.Spinner([
                    dcc.Store('companies'),
                    dcc.Dropdown(
                        id='companies_dropdown',
                        placeholder="Search and select companies",
                        multi=True,
                        searchable=True,
                    ),
                ]),
            ], className="mb-4"),

            html.Div([
                dbc.Spinner(html.Div(id='table_container'))
            ])

        ]),

        dcc.Store('page_loaded')

    ])


def navbar():
    return dbc.NavbarSimple(
        children=[
            dbc.NavItem(dbc.NavLink("Page 1", href="#")),
            dbc.DropdownMenu(
                children=[
                    dbc.DropdownMenuItem("More pages", header=True),
                    dbc.DropdownMenuItem("Page 2", href="#"),
                    dbc.DropdownMenuItem("Page 3", href="#"),
                ],
                nav=True,
                in_navbar=True,
                label="More",
            ),
        ],
        brand="RepLit",
        brand_href="/",
        color="primary",
        dark=True,
    )
