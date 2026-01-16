"""Side charts callbacks (boxplot and other auxiliary charts)."""
from typing import Optional, List

import pandas as pd
import plotly.graph_objects as go
from dash import Input, Output, State, callback_context

from .. import ids
from ..config import config
from ..data.db import get_plot_data


def register_side_charts_callbacks(app):
    """Register callbacks for side charts (boxplot, etc.)."""
    
    # Boxplot mode toggle callback
    @app.callback(
        [
            Output(ids.STORE_BOXPLOT_MODE, "data"),
            Output(ids.BTN_BOXPLOT_BY_OM, "active"),
            Output(ids.BTN_BOXPLOT_BY_DODAVATEL, "active"),
        ],
        [
            Input(ids.BTN_BOXPLOT_BY_OM, "n_clicks"),
            Input(ids.BTN_BOXPLOT_BY_DODAVATEL, "n_clicks"),
        ],
        State(ids.STORE_BOXPLOT_MODE, "data"),
        prevent_initial_call=True,
    )
    def toggle_boxplot_mode(n_om, n_dodavatel, current_mode):
        """Toggle between grouping by location or supplier."""
        ctx = callback_context
        if not ctx.triggered:
            return "om", True, False
        
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]
        if button_id == ids.BTN_BOXPLOT_BY_OM:
            return "om", True, False
        elif button_id == ids.BTN_BOXPLOT_BY_DODAVATEL:
            return "dodavatel", False, True
        return current_mode, current_mode == "om", current_mode == "dodavatel"
    
    # Boxplot outliers toggle callback
    @app.callback(
        [
            Output(ids.STORE_BOXPLOT_OUTLIERS, "data"),
            Output(ids.BTN_BOXPLOT_OUTLIERS, "active"),
        ],
        Input(ids.BTN_BOXPLOT_OUTLIERS, "n_clicks"),
        State(ids.STORE_BOXPLOT_OUTLIERS, "data"),
        prevent_initial_call=True,
    )
    def toggle_boxplot_outliers(n_clicks, current_state):
        """Toggle outliers visibility."""
        new_state = not current_state if current_state is not None else False
        return new_state, new_state
    
    # Boxplot chart callback
    @app.callback(
        Output(ids.CHART_SIDE_TOP, "figure"),
        [
            Input(ids.DROPDOWN_DATASET, "value"),
            Input(ids.DROPDOWN_NUKLID, "value"),
            Input(ids.DROPDOWN_OM, "value"),
            Input(ids.DROPDOWN_DODAVATEL, "value"),
            Input(ids.STORE_SELECTION, "data"),
            Input(ids.SLIDER_DATA_RANGE, "value"),
            Input(ids.STORE_BOXPLOT_MODE, "data"),
            Input(ids.STORE_BOXPLOT_OUTLIERS, "data"),
            Input(ids.STORE_SHOW_MVA, "data"),
        ],
        State(ids.STORE_DATE_RANGE, "data"),
        prevent_initial_call=False,
    )
    def update_boxplot_chart(
        dataset: Optional[str],
        nuklid: Optional[str],
        odber_misto: Optional[List[str]],
        dodavatel: Optional[List[str]],
        selected_keys: Optional[list],
        data_range_slider: Optional[list],
        boxplot_mode: Optional[str],
        show_outliers: Optional[bool],
        show_mva: Optional[bool],
        date_range_store: Optional[dict],
    ):
        """
        Update the boxplot chart based on selection and grouping mode.
        
        Shows boxplots grouped by location (odber_misto) or supplier (dodavatel_dat).
        Always includes a summary boxplot "Vše" for all data.
        If no selection, uses all data. If selection exists, uses selected data.
        When show_mva is False, MVA values are excluded from calculations.
        """
        # Empty figure template
        empty_fig = go.Figure()
        empty_fig.update_layout(
            margin=dict(l=40, r=10, t=30, b=80),
            xaxis_title="",
            yaxis_title="Hodnota",
        )
        
        if not dataset or not nuklid:
            empty_fig.add_annotation(
                text="Vyberte dataset a nuklid",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=12, color="gray"),
            )
            return empty_fig
        
        # Build filters
        filters = {"nuklid": nuklid}
        if odber_misto and len(odber_misto) > 0:
            filters["odber_misto"] = odber_misto
        if dodavatel and len(dodavatel) > 0:
            filters["dodavatel_dat"] = dodavatel
        
        # Load data
        try:
            df = get_plot_data(dataset, filters=filters, max_points=config.database.max_points)
        except Exception as e:
            print(f"Error loading data for boxplot: {e}")
            return empty_fig
        
        if df.empty:
            empty_fig.add_annotation(
                text="Žádná data",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=12, color="gray"),
            )
            return empty_fig
        
        # Apply date range filter
        if "datum" in df.columns and df["datum"].notna().any() and data_range_slider:
            if date_range_store and date_range_store.get("min") and date_range_store.get("max"):
                full_min_date = pd.to_datetime(date_range_store["min"])
                full_max_date = pd.to_datetime(date_range_store["max"])
            else:
                full_min_date = df["datum"].min()
                full_max_date = df["datum"].max()
            
            total_seconds = (full_max_date - full_min_date).total_seconds()
            data_range_start = full_min_date + pd.Timedelta(seconds=total_seconds * data_range_slider[0] / 100)
            data_range_end = full_min_date + pd.Timedelta(seconds=total_seconds * data_range_slider[1] / 100)
            df = df[(df["datum"] >= data_range_start) & (df["datum"] <= data_range_end)]
        
        if df.empty:
            empty_fig.add_annotation(
                text="Žádná data v rozsahu",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=12, color="gray"),
            )
            return empty_fig
        
        # Filter to selected data if selection exists
        selected_set = set(selected_keys) if selected_keys else set()
        if selected_set:
            df_plot = df[df["row_key"].isin(selected_set)].copy()
            if df_plot.empty:
                # Selection exists but no matching data - show all
                df_plot = df.copy()
        else:
            df_plot = df.copy()
        
        # Filter out MVA values if show_mva is False
        # MVA values should not be included in boxplot calculations
        if show_mva is False and "pod_mva" in df_plot.columns:
            df_plot = df_plot[df_plot["pod_mva"] != 1]
            if df_plot.empty:
                empty_fig.add_annotation(
                    text="Žádná data (pouze MVA)",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5, showarrow=False,
                    font=dict(size=12, color="gray"),
                )
                return empty_fig
        
        # Determine grouping column
        group_col = "odber_misto" if boxplot_mode == "om" else "dodavatel_dat"
        group_label = "Odběrové místo" if boxplot_mode == "om" else "Dodavatel"
        
        # Get unit for Y-axis label
        unit = df_plot["jednotka"].iloc[0] if "jednotka" in df_plot.columns and len(df_plot) > 0 else ""
        y_label = f"Hodnota [{unit}]" if unit else "Hodnota"
        
        # Determine boxpoints setting based on outliers toggle
        # "outliers" shows only outliers, "all" shows all points, False hides all points
        boxpoints_setting = "outliers" if show_outliers else False
        
        # Create figure
        fig = go.Figure()
        
        # Add summary boxplot "Vše" first
        fig.add_trace(go.Box(
            y=df_plot["hodnota"],
            name="Vše",
            marker_color=config.boxplot.summary_color,
            boxmean=True,
            boxpoints=boxpoints_setting,
        ))
        
        # Add boxplots for each category
        if group_col in df_plot.columns:
            # Get unique categories sorted by count (most common first)
            category_counts = df_plot[group_col].value_counts()
            categories = category_counts.index.tolist()
            
            # Limit to top N categories if too many
            max_categories = config.boxplot.max_categories
            if len(categories) > max_categories:
                categories = categories[:max_categories]
            
            # Color palette for categories from config
            colors = config.category_colors
            
            for i, cat in enumerate(categories):
                cat_data = df_plot[df_plot[group_col] == cat]["hodnota"]
                if len(cat_data) > 0:
                    # Truncate long category names
                    display_name = str(cat)[:15] + "..." if len(str(cat)) > 15 else str(cat)
                    fig.add_trace(go.Box(
                        y=cat_data,
                        name=display_name,
                        marker_color=colors[i % len(colors)],
                        boxmean=True,
                        boxpoints=boxpoints_setting,
                    ))
        
        # Update layout
        n_selected = len(selected_set) if selected_set else len(df_plot)
        title_text = f"Vybrané ({n_selected})" if selected_set else f"Všechna data ({len(df_plot)})"
        
        fig.update_layout(
            title=dict(
                text=title_text,
                font=dict(size=11),
            ),
            margin=dict(l=50, r=10, t=30, b=100),
            yaxis_title=y_label,
            xaxis_tickangle=-45,
            showlegend=False,
            height=config.layout.boxplot_height,
        )
        
        return fig

    # Histogram chart callback
    @app.callback(
        Output(ids.CHART_SIDE_BOTTOM, "figure"),
        [
            Input(ids.DROPDOWN_DATASET, "value"),
            Input(ids.DROPDOWN_NUKLID, "value"),
            Input(ids.DROPDOWN_OM, "value"),
            Input(ids.DROPDOWN_DODAVATEL, "value"),
            Input(ids.STORE_SELECTION, "data"),
            Input(ids.SLIDER_DATA_RANGE, "value"),
            Input(ids.STORE_SHOW_MVA, "data"),
            Input(ids.SLIDER_HISTOGRAM_BINS, "value"),
        ],
        State(ids.STORE_DATE_RANGE, "data"),
        prevent_initial_call=False,
    )
    def update_histogram_chart(
        dataset: Optional[str],
        nuklid: Optional[str],
        odber_misto: Optional[List[str]],
        dodavatel: Optional[List[str]],
        selected_keys: Optional[list],
        data_range_slider: Optional[list],
        show_mva: Optional[bool],
        n_bins_slider: Optional[int],
        date_range_store: Optional[dict],
    ):
        """
        Update the histogram chart showing distribution of values.
        
        Shows histogram of all filtered data with selected data overlaid.
        """
        # Empty figure template
        empty_fig = go.Figure()
        empty_fig.update_layout(
            margin=dict(l=40, r=10, t=30, b=40),
            xaxis_title="Hodnota",
            yaxis_title="Četnost",
        )
        
        if not dataset or not nuklid:
            empty_fig.add_annotation(
                text="Vyberte dataset a nuklid",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=12, color="gray"),
            )
            return empty_fig
        
        # Build filters
        filters = {"nuklid": nuklid}
        if odber_misto and len(odber_misto) > 0:
            filters["odber_misto"] = odber_misto
        if dodavatel and len(dodavatel) > 0:
            filters["dodavatel_dat"] = dodavatel
        
        # Load data
        try:
            df = get_plot_data(dataset, filters=filters, max_points=config.database.max_points)
        except Exception as e:
            print(f"Error loading data for histogram: {e}")
            return empty_fig
        
        if df.empty:
            empty_fig.add_annotation(
                text="Žádná data",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=12, color="gray"),
            )
            return empty_fig
        
        # Filter out MVA if show_mva is False
        if show_mva is False and "pod_mva" in df.columns:
            df = df[df["pod_mva"] != 1]
            if df.empty:
                empty_fig.add_annotation(
                    text="Žádná data (pouze MVA)",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5, showarrow=False,
                    font=dict(size=12, color="gray"),
                )
                return empty_fig
        
        # Apply date range filter
        if "datum" in df.columns and df["datum"].notna().any() and data_range_slider:
            if date_range_store and date_range_store.get("min") and date_range_store.get("max"):
                full_min_date = pd.to_datetime(date_range_store["min"])
                full_max_date = pd.to_datetime(date_range_store["max"])
            else:
                full_min_date = df["datum"].min()
                full_max_date = df["datum"].max()
            
            total_seconds = (full_max_date - full_min_date).total_seconds()
            data_range_start = full_min_date + pd.Timedelta(seconds=total_seconds * data_range_slider[0] / 100)
            data_range_end = full_min_date + pd.Timedelta(seconds=total_seconds * data_range_slider[1] / 100)
            df = df[(df["datum"] >= data_range_start) & (df["datum"] <= data_range_end)]
        
        if df.empty:
            empty_fig.add_annotation(
                text="Žádná data v rozsahu",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=12, color="gray"),
            )
            return empty_fig
        
        # Get unit for X-axis label
        unit = df["jednotka"].iloc[0] if "jednotka" in df.columns and len(df) > 0 else ""
        x_label = f"Hodnota [{unit}]" if unit else "Hodnota"
        
        # Create figure
        fig = go.Figure()
        
        # Determine selected data
        selected_set = set(selected_keys) if selected_keys else set()
        
        # Calculate common bin edges for both histograms
        all_values = df["hodnota"].dropna()
        if len(all_values) == 0:
            return empty_fig
        
        # Use percentiles to define bin range (ignore extreme outliers)
        import numpy as np
        p1 = np.percentile(all_values, 1)
        p99 = np.percentile(all_values, 99)
        
        # If all values are similar, use min/max
        if p99 <= p1:
            p1 = all_values.min()
            p99 = all_values.max()
        
        # Calculate bin size using slider value
        n_bins = n_bins_slider if n_bins_slider else config.histogram.default_bins
        bin_size = (p99 - p1) / n_bins if p99 > p1 else 1
        
        # Extend range slightly to include edge values
        bin_start = p1 - bin_size * 0.5
        bin_end = p99 + bin_size * 0.5
        
        # Common xbins for both histograms
        xbins_config = dict(start=bin_start, end=bin_end, size=bin_size)
        
        # Add histogram for all data (background, semi-transparent)
        fig.add_trace(go.Histogram(
            x=all_values,
            name="Všechna data",
            marker_color=config.histogram.all_data_color,
            opacity=config.histogram.all_data_opacity,
            xbins=xbins_config,
            bingroup=1,  # Share bins between histograms
        ))
        
        # Add histogram for selected data (overlay, more opaque)
        if selected_set:
            df_selected = df[df["row_key"].isin(selected_set)]
            if not df_selected.empty:
                selected_values = df_selected["hodnota"].dropna()
                if len(selected_values) > 0:
                    fig.add_trace(go.Histogram(
                        x=selected_values,
                        name="Vybrané",
                        marker_color=config.histogram.selected_color,
                        opacity=config.histogram.selected_opacity,
                        xbins=xbins_config,
                        bingroup=1,  # Share bins between histograms
                    ))
        
        # Update layout
        n_all = len(all_values)
        n_selected = len(selected_set) if selected_set else 0
        title_text = f"Histogram ({n_selected}/{n_all})" if selected_set else f"Histogram ({n_all})"
        
        fig.update_layout(
            title=dict(
                text=title_text,
                font=dict(size=11),
            ),
            margin=dict(l=50, r=10, t=30, b=50),
            xaxis_title=x_label,
            yaxis_title="Četnost",
            barmode="overlay",  # Overlay histograms
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="left",
                x=0,
                font=dict(size=9),
            ),
            height=config.layout.histogram_height,
        )
        
        return fig
