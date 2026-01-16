"""Filter dropdown callbacks."""
from typing import Optional

from dash import Input, Output, State, no_update

from .. import ids
from ..data.cache import (
    get_cached_columns,
    get_cached_nuklidy,
    get_cached_odber_mista,
    get_cached_dodavatele,
)
from .status_log import add_log_entry


def register_filter_callbacks(app):
    """Register filter-related callbacks."""
    
    @app.callback(
        [
            Output(ids.DROPDOWN_NUKLID, "options"),
            Output(ids.DROPDOWN_NUKLID, "value"),
            Output(ids.DROPDOWN_OM, "options"),
            Output(ids.DROPDOWN_OM, "value"),
            Output(ids.DROPDOWN_DODAVATEL, "options"),
            Output(ids.DROPDOWN_DODAVATEL, "value"),
            Output(ids.STORE_STATUS_LOG, "data", allow_duplicate=True),
        ],
        Input(ids.DROPDOWN_DATASET, "value"),
        State(ids.STORE_STATUS_LOG, "data"),
        prevent_initial_call=True,
    )
    def update_filter_options(dataset: Optional[str], log_data):
        """Update filter dropdown options when dataset changes (uses cache)."""
        if not dataset:
            return [], None, [], None, [], None, no_update
        
        try:
            columns = get_cached_columns(dataset)
            
            # Nuklid options - default to Cs-137 if available
            default_nuklid = None
            if "nuklid" in columns:
                nuklidy = get_cached_nuklidy(dataset)
                nuklid_options = [{"label": n, "value": n} for n in nuklidy]
                # Try to set Cs-137 as default
                cs137_variants = ["Cs-137", "Cs137", "137Cs", "Cs 137"]
                for variant in cs137_variants:
                    if variant in nuklidy:
                        default_nuklid = variant
                        break
                # If no Cs-137, use first available nuklid
                if default_nuklid is None and nuklidy:
                    default_nuklid = nuklidy[0]
            else:
                nuklid_options = []
            
            # Odběrové místo options (multi-select)
            if "odber_misto" in columns:
                om_values = get_cached_odber_mista(dataset)
                om_options = [{"label": o, "value": o} for o in om_values]
            else:
                om_options = []
            
            # Dodavatel options (multi-select)
            if "dodavatel_dat" in columns:
                dodavatele = get_cached_dodavatele(dataset)
                dodavatel_options = [{"label": d, "value": d} for d in dodavatele]
            else:
                dodavatel_options = []
            
            # Log dataset change
            new_log = add_log_entry(
                log_data, 
                f"Dataset změněn: {dataset}", 
                "success"
            )
            
            return nuklid_options, default_nuklid, om_options, [], dodavatel_options, [], new_log
            
        except Exception as e:
            print(f"Error updating filter options: {e}")
            new_log = add_log_entry(log_data, f"Chyba načítání: {e}", "error")
            return [], None, [], [], [], [], new_log

    @app.callback(
        Output("histogram-bins-value", "children"),
        Input(ids.SLIDER_HISTOGRAM_BINS, "value"),
    )
    def update_histogram_bins_display(value):
        """Display current histogram bins value."""
        return f"Počet: {value}"

    @app.callback(
        Output(ids.STORE_STATUS_LOG, "data", allow_duplicate=True),
        [
            Input(ids.DROPDOWN_NUKLID, "value"),
            Input(ids.DROPDOWN_OM, "value"),
            Input(ids.DROPDOWN_DODAVATEL, "value"),
        ],
        State(ids.STORE_STATUS_LOG, "data"),
        prevent_initial_call=True,
    )
    def log_filter_changes(nuklid, om, dodavatel, log_data):
        """Log when filters are changed."""
        from dash import callback_context
        
        if not callback_context.triggered:
            return no_update
        
        trigger = callback_context.triggered[0]["prop_id"]
        
        if ids.DROPDOWN_NUKLID in trigger and nuklid:
            return add_log_entry(log_data, f"Filtr nuklid: {nuklid}", "info")
        elif ids.DROPDOWN_OM in trigger and om:
            count = len(om) if isinstance(om, list) else 1
            return add_log_entry(log_data, f"Filtr místo: {count} vybráno", "info")
        elif ids.DROPDOWN_DODAVATEL in trigger and dodavatel:
            count = len(dodavatel) if isinstance(dodavatel, list) else 1
            return add_log_entry(log_data, f"Filtr dodavatel: {count} vybráno", "info")
        
        return no_update
