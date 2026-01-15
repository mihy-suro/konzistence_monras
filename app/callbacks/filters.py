"""Filter dropdown callbacks."""
from typing import Optional

from dash import Input, Output

from .. import ids
from ..data.cache import (
    get_cached_columns,
    get_cached_nuklidy,
    get_cached_odber_mista,
    get_cached_dodavatele,
)


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
        ],
        Input(ids.DROPDOWN_DATASET, "value"),
        prevent_initial_call=True,
    )
    def update_filter_options(dataset: Optional[str]):
        """Update filter dropdown options when dataset changes (uses cache)."""
        if not dataset:
            return [], None, [], None, [], None
        
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
            
            return nuklid_options, default_nuklid, om_options, [], dodavatel_options, []
            
        except Exception as e:
            print(f"Error updating filter options: {e}")
            return [], None, [], [], [], []
