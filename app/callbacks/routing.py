"""Routing and config editor callbacks."""
from pathlib import Path

import yaml
from dash import Input, Output, State, html, no_update
import dash_bootstrap_components as dbc

from .. import ids
from ..pages import create_home_page, create_docs_page, create_config_page
from ..config import reload_config, get_config_path
from ..data.cache import clear_cache


def register_routing_callbacks(app):
    """Register routing and config editor callbacks."""
    
    @app.callback(
        Output(ids.PAGE_CONTENT, "children"),
        Input(ids.URL_LOCATION, "pathname"),
    )
    def render_page(pathname):
        """Route to the correct page based on URL."""
        if pathname == "/docs":
            return create_docs_page()
        elif pathname == "/config":
            return create_config_page()
        else:
            # Default to home page
            return create_home_page()
    
    # Config content is now loaded directly in the page component
    # No separate callback needed for initial load
    
    @app.callback(
        Output(ids.CONFIG_STATUS, "children"),
        Input(ids.BTN_CONFIG_SAVE, "n_clicks"),
        State(ids.CONFIG_EDITOR, "value"),
        prevent_initial_call=True,
    )
    def save_config(n_clicks, content):
        """Save config.yaml content."""
        if not n_clicks or not content:
            return no_update
        
        # Validate YAML syntax first
        try:
            yaml.safe_load(content)
        except yaml.YAMLError as e:
            return dbc.Alert(
                [
                    html.I(className="bi bi-exclamation-triangle me-2"),
                    f"Chyba YAML syntaxe: {e}",
                ],
                color="danger",
                className="mb-0",
            )
        
        # Save to file
        config_path = get_config_path()
        try:
            with open(config_path, "w", encoding="utf-8") as f:
                f.write(content)
            return dbc.Alert(
                [
                    html.I(className="bi bi-check-circle me-2"),
                    "Konfigurace uložena. Klikněte na 'Reload' pro aplikování změn.",
                ],
                color="success",
                className="mb-0",
            )
        except Exception as e:
            return dbc.Alert(
                [
                    html.I(className="bi bi-exclamation-triangle me-2"),
                    f"Chyba při ukládání: {e}",
                ],
                color="danger",
                className="mb-0",
            )
    
    @app.callback(
        Output(ids.CONFIG_STATUS, "children", allow_duplicate=True),
        Input(ids.BTN_CONFIG_RELOAD, "n_clicks"),
        prevent_initial_call=True,
    )
    def reload_app_config(n_clicks):
        """Reload configuration and clear cache."""
        if not n_clicks:
            return no_update
        
        try:
            # Reload config
            reload_config()
            # Clear data cache so new prefilters take effect
            clear_cache()
            
            return dbc.Alert(
                [
                    html.I(className="bi bi-check-circle me-2"),
                    "Konfigurace načtena. ",
                    html.A("Přejít na hlavní stránku", href="/", className="alert-link"),
                    " pro zobrazení změn.",
                ],
                color="info",
                className="mb-0",
            )
        except Exception as e:
            return dbc.Alert(
                [
                    html.I(className="bi bi-exclamation-triangle me-2"),
                    f"Chyba při načítání konfigurace: {e}",
                ],
                color="danger",
                className="mb-0",
            )
