"""
Callbacks pro detekci a zobrazení outlierů.

Funkce:
- Spuštění detekce outlierů podle vybrané metody
- Aktualizace parametrů detekce (threshold, multiplier)
- Vizualizace outlierů v grafech (zvýraznění bodů)
- Aktualizace tabulky s detekovanými outliery
- Export outlierů do souboru

Používá služby z app.services.outlier_detection.
"""

# from dash import Input, Output, State, callback
# from app.server import app
# from app.services.outlier_detection import detect_outliers_iqr, detect_outliers_zscore


# TODO: Implementovat callbacks pro outliery
# @app.callback(
#     Output("outliers-table", "data"),
#     Output("outliers-chart", "figure"),
#     Input("detection-method", "value"),
#     Input("threshold-slider", "value"),
#     State("data-store", "data"),
# )
# def detect_and_display_outliers(method, threshold, data):
#     ...
