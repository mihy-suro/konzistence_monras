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
        ],
        State(ids.STORE_SELECTION, "data"),
        prevent_initial_call=True,
    )
    def update_selection_store(
        selected_data: Optional[dict],
        reset_clicks: Optional[int],
        dataset: Optional[str],
        current_selection: list,
    ):
        """
        Update selection store based on graph selection or reset.
        """
        triggered_id = ctx.triggered_id
        
        # Reset button or dataset change clears selection
        if triggered_id == ids.BTN_RESET or triggered_id == ids.DROPDOWN_DATASET:
            return []
        
        # GUARD: If triggered by scatter plot but selectedData is None/empty,
        # this is likely a side-effect of figure redraw - do NOT update Store
        if triggered_id == ids.SCATTER_PLOT:
            if not selected_data or "points" not in selected_data or not selected_data["points"]:
                return no_update
            
            # Extract keys from valid scatter selection
            selected_keys = []
            for point in selected_data["points"]:
                if "customdata" in point and point["customdata"]:
                    if isinstance(point["customdata"], list):
                        selected_keys.append(point["customdata"][0])
                    else:
                        selected_keys.append(point["customdata"])
            return selected_keys
        
        return no_update
