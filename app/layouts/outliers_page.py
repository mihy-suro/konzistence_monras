"""
Stránka pro detekci a vizualizaci outlierů.

Poskytuje:
- Výběr metody detekce (IQR, Z-score, Isolation Forest)
- Nastavení parametrů detekce (threshold, multiplier)
- Vizualizace outlierů v datech (box plot, scatter)
- Tabulka s detekovanými outliery
- Export outlierů do CSV/Excel

Umožňuje uživateli identifikovat anomálie v měřeních.
"""

from dash import html
import dash_bootstrap_components as dbc


def create_outliers_layout() -> dbc.Container:
    """
    Vytvoří layout stránky pro detekci outlierů.
    
    Returns:
        dbc.Container s outlier detekcí
    """
    # TODO: Implementovat outliers layout
    return dbc.Container(
        [
            html.H2("Detekce outlierů"),
            html.Hr(),
            # Nastavení metody
            # Vizualizace
            # Tabulka outlierů
        ]
    )
