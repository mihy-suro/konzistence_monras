"""
Callbacks modul - interaktivita aplikace.

Každý modul obsahuje callbacks (@app.callback dekorátory) pro specifickou
funkcionalitu. Callbacks se registrují automaticky při importu modulu.

DŮLEŽITÉ: Callbacks importují `app` ze `server.py`, nikdy z `main.py`!

Moduly:
    - upload_callbacks: Zpracování nahraných souborů
    - filter_callbacks: Filtrování dat podle uživatelských kritérií
    - chart_callbacks: Crossfiltering a aktualizace grafů
    - outlier_callbacks: Detekce a zobrazení outlierů
"""

# Import modulů pro registraci callbacks
from . import upload_callbacks  # noqa: F401
from . import filter_callbacks  # noqa: F401
from . import chart_callbacks  # noqa: F401
from . import outlier_callbacks  # noqa: F401
