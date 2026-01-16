"""
MRS Viewer - Dash Application Instance

MVP version with scatter plot crossfiltering to AG Grid table.
"""
import dash
import dash_bootstrap_components as dbc

from .data.cache import init_cache
from .layout import create_layout
from .callbacks import register_callbacks

# Initialize filter cache at startup (pre-loads all dropdown values)
print("Starting MRS Viewer...")
init_cache()

# Initialize Dash app with Bootstrap theme
app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        dbc.icons.BOOTSTRAP,  # Bootstrap Icons for navbar
    ],
    title="MRS Viewer",
    update_title="Načítání...",
    suppress_callback_exceptions=True,
)

# Set layout
app.layout = create_layout()

# Register callbacks
register_callbacks(app)

# Expose server for production deployments (e.g., gunicorn)
server = app.server
