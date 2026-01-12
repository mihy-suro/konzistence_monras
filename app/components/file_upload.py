"""
Komponenta pro nahrávání souborů.

Vytváří stylizovanou drag & drop zónu pro nahrání xlsx souborů.
Podporuje:
- Drag & drop
- Click pro výběr souboru
- Validaci typu souboru (pouze .xlsx)
- Zobrazení názvu nahraného souboru
"""

from dash import html, dcc
import dash_bootstrap_components as dbc


def create_upload_component(component_id: str = "upload-excel") -> html.Div:
    """
    Vytvoří upload komponentu pro Excel soubory.
    
    Args:
        component_id: ID komponenty pro callbacks
        
    Returns:
        html.Div s dcc.Upload komponentou
    """
    # TODO: Implementovat upload komponentu
    return html.Div(
        [
            dcc.Upload(
                id=component_id,
                children=html.Div([
                    "Přetáhněte soubor nebo ",
                    html.A("klikněte pro výběr"),
                ]),
                style={
                    "width": "100%",
                    "height": "60px",
                    "lineHeight": "60px",
                    "borderWidth": "1px",
                    "borderStyle": "dashed",
                    "borderRadius": "5px",
                    "textAlign": "center",
                },
                accept=".xlsx",
            ),
        ]
    )
