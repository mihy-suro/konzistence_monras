"""
Centrální Dash aplikace - sdílená instance.

Tento modul vytváří a exportuje jedinou instanci Dash aplikace,
kterou importují všechny ostatní moduly. Tím se předchází circular imports.

Použití:
    from app.server import app
    
    @app.callback(...)
    def my_callback(...):
        ...
"""

import dash
import dash_bootstrap_components as dbc

# Centrální instance Dash aplikace
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,  # Pro dynamické layouty
    title="MonRaS - Konzistence dat",
    update_title="Načítám...",
)

# WSGI server pro produkční nasazení
server = app.server
