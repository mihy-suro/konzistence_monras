"""
Stránka pro nahrávání Excel souborů.

Poskytuje:
- Drag & drop zónu pro nahrání xlsx souborů
- Náhled načtených dat (prvních N řádků)
- Informace o souboru (počet řádků, sloupců, datové typy)
- Validační hlášky (úspěch/chyba při parsování)

Po úspěšném nahrání jsou data uložena do dcc.Store
a uživatel může přejít na stránku Analýza.
"""

from dash import html, dcc
import dash_bootstrap_components as dbc


def create_upload_layout() -> dbc.Container:
    """
    Vytvoří layout stránky pro upload souborů.
    
    Returns:
        dbc.Container s upload komponentami
    """
    # TODO: Implementovat upload layout
    return dbc.Container(
        [
            html.H2("Nahrát Excel soubor"),
            html.Hr(),
            # Upload komponenta
            # Preview tabulka
            # Info panel
        ]
    )
