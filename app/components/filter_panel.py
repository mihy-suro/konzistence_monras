"""
Komponenta pro panel filtrů.

Vytváří panel s:
- Dropdown filtry pro kategorické sloupce
- Range slidery pro numerické sloupce
- Date pickery pro datumové sloupce
- Tlačítko pro reset filtrů

Filtry se dynamicky generují podle typu sloupců v datech.
"""

from dash import html
import dash_bootstrap_components as dbc


def create_filter_panel(component_id: str = "filter-panel") -> dbc.Card:
    """
    Vytvoří panel s filtry.
    
    Args:
        component_id: ID komponenty pro callbacks
        
    Returns:
        dbc.Card s filtry
    """
    # TODO: Implementovat filter panel
    return dbc.Card(
        [
            dbc.CardHeader("Filtry"),
            dbc.CardBody(
                [
                    html.Div(id=f"{component_id}-content"),
                    dbc.Button(
                        "Resetovat filtry",
                        id=f"{component_id}-reset",
                        color="secondary",
                        className="mt-3",
                    ),
                ]
            ),
        ],
        id=component_id,
    )
