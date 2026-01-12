"""
Services modul - business logika a data processing.

Služby jsou čisté Python funkce bez závislosti na Dash.
Snadno testovatelné a znovupoužitelné.

Moduly:
    - data_store: Správa dat v paměti, serializace pro dcc.Store
    - statistics: Výpočty statistik (průměr, medián, std, ...)
    - outlier_detection: Detekce outlierů (IQR, Z-score, Isolation Forest)
"""

from .statistics import calculate_statistics, calculate_column_stats
from .outlier_detection import detect_outliers_iqr, detect_outliers_zscore

__all__ = [
    "calculate_statistics",
    "calculate_column_stats",
    "detect_outliers_iqr",
    "detect_outliers_zscore",
]
