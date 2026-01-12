"""
Komponenta pro statistické karty.

Zobrazuje souhrnné statistiky dat v kartách:
- Počet záznamů
- Průměr, medián, směrodatná odchylka
- Minimum, maximum
- Počet chybějících hodnot
- Počet outlierů

Karty se aktualizují podle vybraného sloupce a filtrů.
"""

from dash import html
import dash_bootstrap_components as dbc


def create_stat_cards(component_id: str = "stat-cards") -> dbc.Row:
    """
    Vytvoří řadu karet se statistikami.
    
    Args:
        component_id: ID komponenty pro callbacks
        
    Returns:
        dbc.Row s kartami statistik
    """
    # TODO: Implementovat stat cards
    return dbc.Row(
        [
            dbc.Col(_create_stat_card("Počet záznamů", "-", f"{component_id}-count")),
            dbc.Col(_create_stat_card("Průměr", "-", f"{component_id}-mean")),
            dbc.Col(_create_stat_card("Medián", "-", f"{component_id}-median")),
            dbc.Col(_create_stat_card("Std", "-", f"{component_id}-std")),
        ],
        id=component_id,
    )


def _create_stat_card(title: str, value: str, card_id: str) -> dbc.Card:
    """Vytvoří jednu statistickou kartu."""
    return dbc.Card(
        [
            dbc.CardBody(
                [
                    html.H6(title, className="card-subtitle text-muted"),
                    html.H4(value, id=card_id, className="card-title"),
                ]
            )
        ],
        className="text-center",
    )
