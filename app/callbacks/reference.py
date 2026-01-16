"""Reference period and data range slider callbacks."""
from typing import Optional, List

import pandas as pd
from dash import Input, Output, State, clientside_callback, ClientsideFunction

from .. import ids


def register_reference_callbacks(app):
    """Register reference period control callbacks."""
    
    # Clientside callback to update JavaScript date range for slider tooltips
    clientside_callback(
        """
        function(dateRange) {
            if (dateRange && dateRange.min && dateRange.max) {
                window.sliderDateRanges = window.sliderDateRanges || {};
                window.sliderDateRanges.dataRange = {
                    min: dateRange.min,
                    max: dateRange.max
                };
            }
            return '';
        }
        """,
        Output(ids.DUMMY_DATE_RANGE_SYNC, "children"),
        Input(ids.STORE_DATE_RANGE, "data"),
        prevent_initial_call=True,
    )
    
    @app.callback(
        Output(ids.STORE_DATE_RANGE, "data"),
        [
            Input(ids.DROPDOWN_DATASET, "value"),
            Input(ids.DROPDOWN_NUKLID, "value"),
            Input(ids.DROPDOWN_OM, "value"),
            Input(ids.DROPDOWN_DODAVATEL, "value"),
        ],
        prevent_initial_call=True,
    )
    def update_date_range_from_filters(
        dataset: Optional[str],
        nuklid: Optional[str],
        odber_misto: Optional[List[str]],
        dodavatel: Optional[List[str]],
    ):
        """
        Update date range store when dataset or filters change.
        
        Queries the database for min/max dates with current filters applied.
        """
        from ..data.db import get_plot_data
        
        if not dataset or not nuklid:
            return {"min": None, "max": None}
        
        try:
            # Build filters
            filters = {"nuklid": nuklid}
            if odber_misto and len(odber_misto) > 0:
                filters["odber_misto"] = odber_misto
            if dodavatel and len(dodavatel) > 0:
                filters["dodavatel_dat"] = dodavatel
            
            # Load data with filters to get actual date range
            df = get_plot_data(dataset, filters=filters, max_points=50000)
            if df.empty or "datum" not in df.columns:
                return {"min": None, "max": None}
            
            min_date = df["datum"].min()
            max_date = df["datum"].max()
            
            if pd.isna(min_date) or pd.isna(max_date):
                return {"min": None, "max": None}
            
            # Store as ISO strings
            return {
                "min": min_date.isoformat(),
                "max": max_date.isoformat(),
            }
        except Exception as e:
            print(f"Error getting date range: {e}")
            return {"min": None, "max": None}
    
    @app.callback(
        Output("data-range-dates", "children"),
        [
            Input(ids.SLIDER_DATA_RANGE, "value"),
            Input(ids.STORE_DATE_RANGE, "data"),
        ],
    )
    def update_data_range_display(slider_value: list, date_range: dict):
        """Display dates for data range slider."""
        if not slider_value or not date_range:
            return ""
        
        min_str = date_range.get("min")
        max_str = date_range.get("max")
        
        if not min_str or not max_str:
            return ""
        
        try:
            min_date = pd.to_datetime(min_str)
            max_date = pd.to_datetime(max_str)
            total_seconds = (max_date - min_date).total_seconds()
            
            start_date = min_date + pd.Timedelta(seconds=total_seconds * slider_value[0] / 100)
            end_date = min_date + pd.Timedelta(seconds=total_seconds * slider_value[1] / 100)
            
            return f"{start_date.strftime('%Y-%m-%d')} → {end_date.strftime('%Y-%m-%d')}"
        except:
            return ""
    
    @app.callback(
        Output("ref-period-dates", "children"),
        [
            Input(ids.SLIDER_REF_PERIOD, "value"),
            Input(ids.STORE_DATE_RANGE, "data"),
        ],
    )
    def update_ref_period_display(slider_value: list, date_range: dict):
        """Display dates for reference period slider."""
        if not slider_value or not date_range:
            return ""
        
        min_str = date_range.get("min")
        max_str = date_range.get("max")
        
        if not min_str or not max_str:
            return ""
        
        try:
            min_date = pd.to_datetime(min_str)
            max_date = pd.to_datetime(max_str)
            total_seconds = (max_date - min_date).total_seconds()
            
            start_date = min_date + pd.Timedelta(seconds=total_seconds * slider_value[0] / 100)
            end_date = min_date + pd.Timedelta(seconds=total_seconds * slider_value[1] / 100)
            
            return f"{start_date.strftime('%Y-%m-%d')} → {end_date.strftime('%Y-%m-%d')}"
        except:
            return ""
