"""
Charts modul - definice Altair/Vega grafů.

Moduly obsahují funkce pro generování Altair specifikací grafů.
Grafy jsou navrženy pro crossfiltering - sdílejí selection objekty.

Moduly:
    - base_chart: Základní konfigurace a témata
    - scatter_chart: Bodové grafy (scatter plots)
    - histogram_chart: Histogramy a distribuce
    - time_series_chart: Časové řady
    - crossfilter: Utility pro propojení grafů
"""

from .crossfilter import create_crossfilter_charts
from .scatter_chart import create_scatter_chart
from .histogram_chart import create_histogram_chart
from .time_series_chart import create_time_series_chart

__all__ = [
    "create_crossfilter_charts",
    "create_scatter_chart",
    "create_histogram_chart",
    "create_time_series_chart",
]
