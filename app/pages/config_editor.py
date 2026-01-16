"""
Configuration editor page - Edit config.yaml and reload application.
"""
import dash_bootstrap_components as dbc
from dash import dcc, html

from .. import ids
from ..config import get_config_path


def _load_config_content() -> str:
    """Load config file content for initial display."""
    config_path = get_config_path()
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"# Error loading config: {e}"

def create_config_page() -> dbc.Container:
    """Create the configuration editor page."""
    return dbc.Container(
        [
            dbc.Row(
                dbc.Col(
                    [
                        html.H3("Nastavení aplikace", className="mb-3"),
                        html.P(
                            "Editujte konfigurační soubor config.yaml. Po uložení změn klikněte na 'Reload' pro aplikování.",
                            className="text-muted",
                        ),
                    ],
                    width=12,
                ),
                className="mb-3",
            ),
            dbc.Row(
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardHeader(
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            html.Span("config.yaml", className="fw-bold"),
                                        ),
                                        dbc.Col(
                                            dbc.ButtonGroup(
                                                [
                                                    dbc.Button(
                                                        [html.I(className="bi bi-arrow-clockwise me-1"), "Reload"],
                                                        id=ids.BTN_CONFIG_RELOAD,
                                                        color="primary",
                                                        size="sm",
                                                    ),
                                                    dbc.Button(
                                                        [html.I(className="bi bi-save me-1"), "Uložit"],
                                                        id=ids.BTN_CONFIG_SAVE,
                                                        color="success",
                                                        size="sm",
                                                    ),
                                                ],
                                            ),
                                            width="auto",
                                        ),
                                    ],
                                    className="align-items-center",
                                ),
                            ),
                            dbc.CardBody(
                                [
                                    dcc.Textarea(
                                        id=ids.CONFIG_EDITOR,
                                        value=_load_config_content(),
                                        style={
                                            "width": "100%",
                                            "height": "600px",
                                            "fontFamily": "monospace",
                                            "fontSize": "13px",
                                        },
                                        spellCheck=False,
                                    ),
                                    # Status message
                                    html.Div(
                                        id=ids.CONFIG_STATUS,
                                        className="mt-2",
                                    ),
                                ],
                            ),
                        ],
                    ),
                    width=12,
                ),
            ),
            # Store for tracking if content was loaded
            dcc.Store(id=ids.STORE_CONFIG_LOADED, data=False),
        ],
        fluid=True,
    )
