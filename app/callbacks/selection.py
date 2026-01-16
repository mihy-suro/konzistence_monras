"""Selection handling callbacks."""
from typing import Optional

from dash import Input, Output, State, ctx, no_update

from .. import ids


def register_selection_callbacks(app):
    """Register selection-related callbacks."""
    
    @app.callback(
        Output(ids.STORE_SELECTION, "data"),
        [
            Input(ids.SCATTER_PLOT, "selectedData"),
            Input(ids.BTN_RESET, "n_clicks"),
            Input(ids.DROPDOWN_DATASET, "value"),
            Input(ids.DROPDOWN_NUKLID, "value"),
            Input(ids.DROPDOWN_OM, "value"),
            Input(ids.DROPDOWN_DODAVATEL, "value"),
        ],
        State(ids.STORE_SELECTION, "data"),
        prevent_initial_call=True,
    )
    def update_selection_store(
        selected_data: Optional[dict],
        reset_clicks: Optional[int],
        dataset: Optional[str],
        nuklid: Optional[str],
        odber_misto: Optional[list],
        dodavatel: Optional[list],
        current_selection: list,
    ):
        """
        Update selection store based on graph selection or reset.
        
        Clears selection when:
        - Reset button is clicked
        - Any filter dropdown changes (dataset, nuklid, odber_misto, dodavatel)
        
        New box selection always replaces previous selection completely.
        """
        triggered_id = ctx.triggered_id
        
        # Reset button or any filter change clears selection
        if triggered_id in [
            ids.BTN_RESET,
            ids.DROPDOWN_DATASET,
            ids.DROPDOWN_NUKLID,
            ids.DROPDOWN_OM,
            ids.DROPDOWN_DODAVATEL,
        ]:
            return []
        
        # Selection box (selectedData)
        if triggered_id == ids.SCATTER_PLOT:
            if not selected_data or "points" not in selected_data or not selected_data["points"]:
                # Empty selection from figure redraw - keep current
                return no_update
            
            # Extract keys from valid scatter selection - this REPLACES previous selection
            selected_keys = []
            for point in selected_data["points"]:
                if "customdata" in point and point["customdata"]:
                    if isinstance(point["customdata"], list):
                        selected_keys.append(point["customdata"][0])
                    else:
                        selected_keys.append(point["customdata"])
            return selected_keys
        
        return no_update
