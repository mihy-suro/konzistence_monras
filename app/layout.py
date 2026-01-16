"""
Layout definition for MRS Viewer MVP.

Defines the top-level app structure with routing support.
"""
import dash_bootstrap_components as dbc
from dash import dcc, html

from . import ids


def create_navbar() -> dbc.Navbar:
    """Create the top navigation bar."""
    return dbc.Navbar(
        dbc.Container(
            [
                # Brand/Logo
                dbc.NavbarBrand(
                    [
                        html.I(className="bi bi-radioactive me-2"),
                        "MRS Viewer",
                    ],
                    href="/",
                    className="fw-bold",
                ),
                
                # Toggle for mobile
                dbc.NavbarToggler(id="navbar-toggler"),
                
                # Navigation links
                dbc.Collapse(
                    dbc.Nav(
                        [
                            dbc.NavItem(
                                dbc.NavLink(
                                    [html.I(className="bi bi-book me-1"), "Návod"],
                                    href="/docs",
                                    external_link=False,
                                ),
                            ),
                            dbc.NavItem(
                                dbc.NavLink(
                                    [html.I(className="bi bi-gear me-1"), "Nastavení"],
                                    href="/config",
                                    external_link=False,
                                ),
                            ),
                            dbc.NavItem(
                                dbc.NavLink(
                                    [html.I(className="bi bi-github me-1"), "GitHub"],
                                    href="https://github.com/your-org/konzistence-monras",
                                    target="_blank",
                                    external_link=True,
                                ),
                            ),
                        ],
                        className="ms-auto",
                        navbar=True,
                    ),
                    id="navbar-collapse",
                    navbar=True,
                ),
            ],
            fluid=True,
        ),
        color="primary",
        dark=True,
        className="mb-3",
    )


def create_layout() -> html.Div:
    """Create the main application layout with routing support."""
    return html.Div(
        [
            # URL location for routing
            dcc.Location(id=ids.URL_LOCATION, refresh=False),
            
            # Top navigation bar (always visible)
            create_navbar(),
            
            # Page content (rendered by routing callback)
            html.Div(id=ids.PAGE_CONTENT),
        ],
    )
