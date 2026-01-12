"""
Components modul - znovupoužitelné UI komponenty.

Komponenty jsou funkce vracející Dash komponenty. Jsou navrženy pro
znovupoužití napříč různými layouty. Neobsahují callbacks - pouze UI.

Moduly:
    - file_upload: Komponenta pro drag & drop nahrávání souborů
    - data_table: Interaktivní tabulka s daty (AG Grid wrapper)
    - filter_panel: Panel s filtry pro data
    - stat_cards: Karty zobrazující statistiky
"""

from .file_upload import create_upload_component
from .data_table import create_data_table
from .filter_panel import create_filter_panel
from .stat_cards import create_stat_cards

__all__ = [
    "create_upload_component",
    "create_data_table",
    "create_filter_panel",
    "create_stat_cards",
]
