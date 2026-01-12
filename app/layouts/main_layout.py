"""
Hlavní layout aplikace.

Definuje:
- Navigační lištu s přepínáním mezi stránkami
- Kontejner pro obsah stránek
- Globální dcc.Store komponenty pro sdílení dat mezi stránkami

Layout používá Bootstrap grid systém pro responzivní design.
"""

from dash import html, dcc
import dash_bootstrap_components as dbc


def create_layout() -> dbc.Container:
    """
    Vytvoří hlavní layout aplikace.
    
    Returns:
        dbc.Container s kompletním layoutem
    """
    return dbc.Container(
        [
            # Globální úložiště dat (session storage)
            dcc.Store(id="data-store", storage_type="session"),
            dcc.Store(id="metadata-store", storage_type="session"),
            
            # Navigace
            _create_navbar(),
            
            # Hlavní obsah
            html.Div(id="page-content", className="mt-4"),
        ],
        fluid=True,
    )


def _create_navbar() -> dbc.Navbar:
    """Vytvoří navigační lištu."""
    return dbc.Navbar(
        dbc.Container(
            [
                dbc.NavbarBrand("MonRaS Konzistence", href="/"),
                dbc.Nav(
                    [
                        dbc.NavItem(dbc.NavLink("Nahrát data", href="/upload")),
                        dbc.NavItem(dbc.NavLink("Analýza", href="/analysis")),
                        dbc.NavItem(dbc.NavLink("Outliery", href="/outliers")),
                    ],
                    navbar=True,
                ),
            ],
            fluid=True,
        ),
        color="primary",
        dark=True,
        className="mb-4",
    )
