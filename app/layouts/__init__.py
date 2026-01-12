"""
Layouts modul - definice stránek a layoutů aplikace.

Každý layout je funkce vracející Dash komponenty (html.Div, dbc.Container, ...).
Layouty NEIMPORTUJÍ callbacks - pouze definují strukturu UI.

Moduly:
    - main_layout: Hlavní layout s navigací a obsahem
    - upload_page: Stránka pro nahrávání Excel souborů
    - analysis_page: Stránka s grafy a analýzou dat
    - outliers_page: Stránka pro detekci a vizualizaci outlierů
"""

from .main_layout import create_layout

__all__ = ["create_layout"]
