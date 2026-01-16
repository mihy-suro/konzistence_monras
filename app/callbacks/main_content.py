"""Main content rendering callback (scatter plot + table)."""
from typing import Optional, List

import pandas as pd
import plotly.graph_objects as go
from dash import Input, Output, State, callback_context

from .. import ids
from ..config import config
from ..data.db import get_plot_data
from ..stats import calculate_tolerance_intervals


def register_main_callbacks(app):
    """Register main content rendering callback."""
    
    # Y-axis zoom button callback
    @app.callback(
        [
            Output(ids.STORE_Y_ZOOM, "data"),
            Output(ids.BTN_ZOOM_2TI, "active"),
            Output(ids.BTN_ZOOM_1TI, "active"),
            Output(ids.BTN_ZOOM_FULL, "active"),
        ],
        [
            Input(ids.BTN_ZOOM_2TI, "n_clicks"),
            Input(ids.BTN_ZOOM_1TI, "n_clicks"),
            Input(ids.BTN_ZOOM_FULL, "n_clicks"),
        ],
        prevent_initial_call=True,
    )
    def update_y_zoom(n_2ti, n_1ti, n_full):
        """Update Y zoom mode based on button clicks."""
        ctx = callback_context
        if not ctx.triggered:
            return "2ti", True, False, False
        
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]
        if button_id == ids.BTN_ZOOM_2TI:
            return "2ti", True, False, False
        elif button_id == ids.BTN_ZOOM_1TI:
            return "1ti", False, True, False
        elif button_id == ids.BTN_ZOOM_FULL:
            return "full", False, False, True
        return "2ti", True, False, False
    
    # MVA toggle callback
    @app.callback(
        [
            Output(ids.STORE_SHOW_MVA, "data"),
            Output(ids.BTN_SHOW_MVA, "active"),
            Output(ids.BTN_SHOW_MVA, "children"),
            Output(ids.BTN_SHOW_MVA, "color"),
        ],
        Input(ids.BTN_SHOW_MVA, "n_clicks"),
        State(ids.STORE_SHOW_MVA, "data"),
        prevent_initial_call=True,
    )
    def toggle_show_mva(n_clicks, current_state):
        """Toggle MVA visibility."""
        new_state = not current_state if current_state is not None else False
        if new_state:
            return new_state, True, "MVA: Zobrazeno", "success"
        else:
            return new_state, False, "MVA: Skryto", "secondary"
    
    @app.callback(
        [
            Output(ids.SCATTER_PLOT, "figure"),
            Output(ids.AGGRID_TABLE, "rowData"),
            Output(ids.INFO_TEXT, "children"),
            Output(ids.TI_INFO, "children"),
            Output(ids.TABLE_STATS, "children"),
        ],
        [
            Input(ids.DROPDOWN_DATASET, "value"),
            Input(ids.DROPDOWN_NUKLID, "value"),
            Input(ids.DROPDOWN_OM, "value"),
            Input(ids.DROPDOWN_DODAVATEL, "value"),
            Input(ids.STORE_SELECTION, "data"),
            Input(ids.SLIDER_DATA_RANGE, "value"),
            Input(ids.SLIDER_REF_PERIOD, "value"),
            Input(ids.STORE_Y_ZOOM, "data"),
            Input(ids.STORE_SHOW_MVA, "data"),
        ],
        State(ids.STORE_DATE_RANGE, "data"),
        prevent_initial_call=False,
    )
    def update_main_content(
        dataset: Optional[str],
        nuklid: Optional[str],
        odber_misto: Optional[List[str]],  # Multi-select returns list
        dodavatel: Optional[List[str]],    # Multi-select returns list
        selected_keys: Optional[list],
        data_range_slider: Optional[list],
        ref_period_slider: Optional[list],
        y_zoom_mode: Optional[str],
        show_mva: Optional[bool],
        date_range_store: Optional[dict],
    ):
        """
        Main callback for scatter plot and table rendering.
        
        - Loads data from DB with filters (supports multi-select)
        - Filters by data range slider
        - Calculates tolerance intervals from reference period slider
        - Renders scatter plot with selection highlighting, reference rectangle, and MVA markers
        - Renders table with selected/all data
        """
        # Default show_mva to True if not set
        if show_mva is None:
            show_mva = True
            
        # Empty state
        empty_fig = go.Figure()
        empty_fig.update_layout(
            xaxis_title="Datum",
            yaxis_title="Hodnota",
            margin=dict(l=50, r=10, t=40, b=30),
        )
        
        if not dataset:
            empty_fig.update_layout(title="Vyberte dataset")
            return empty_fig, [], "Vyberte dataset pro zobrazení dat.", "", ""
        
        # Require nuklid selection for large datasets - prevents loading all data
        if not nuklid:
            empty_fig.update_layout(title="Vyberte nuklid pro zobrazení dat")
            return empty_fig, [], "Vyberte nuklid pro načtení dat.", "", ""
        
        # Build filters dict (multi-select values are lists)
        filters = {}
        if nuklid:
            filters["nuklid"] = nuklid
        if odber_misto and len(odber_misto) > 0:
            filters["odber_misto"] = odber_misto  # List for IN clause
        if dodavatel and len(dodavatel) > 0:
            filters["dodavatel_dat"] = dodavatel  # List for IN clause
        
        # Load data
        try:
            df = get_plot_data(dataset, filters=filters, max_points=50000)
        except Exception as e:
            print(f"Error loading data: {e}")
            return empty_fig, [], f"Chyba při načítání dat: {e}", "", ""
        
        if df.empty:
            empty_fig.update_layout(title="Žádná data pro vybrané filtry")
            return empty_fig, [], "Žádná data odpovídající filtrům.", "", ""
        
        # Filter out MVA if show_mva is False
        if not show_mva and "pod_mva" in df.columns:
            df = df[df["pod_mva"] != 1]
            if df.empty:
                empty_fig.update_layout(title="Žádná data (pouze MVA)")
                return empty_fig, [], "Všechna data jsou pod MVA.", "", ""
        
        total_points_before_filter = len(df)
        selected_set = set(selected_keys) if selected_keys else set()
        
        # Prepare datetime column
        if "datum" in df.columns:
            df["datum_display"] = df["datum"].dt.strftime("%Y-%m-%d %H:%M")
        else:
            df["datum_display"] = "N/A"
        
        # Calculate date boundaries from sliders
        data_range_start = None
        data_range_end = None
        ref_line_start = None
        ref_line_end = None
        
        if "datum" in df.columns and df["datum"].notna().any():
            # Use store date range if available, otherwise calculate from data
            if date_range_store and date_range_store.get("min") and date_range_store.get("max"):
                full_min_date = pd.to_datetime(date_range_store["min"])
                full_max_date = pd.to_datetime(date_range_store["max"])
            else:
                full_min_date = df["datum"].min()
                full_max_date = df["datum"].max()
            
            total_seconds = (full_max_date - full_min_date).total_seconds()
            
            # Data range slider -> filter displayed data
            if data_range_slider:
                data_range_start = full_min_date + pd.Timedelta(seconds=total_seconds * data_range_slider[0] / 100)
                data_range_end = full_min_date + pd.Timedelta(seconds=total_seconds * data_range_slider[1] / 100)
                
                # Filter data by data range slider
                df = df[(df["datum"] >= data_range_start) & (df["datum"] <= data_range_end)]
            
            # Reference period slider -> for TI calculation
            if ref_period_slider:
                ref_line_start = full_min_date + pd.Timedelta(seconds=total_seconds * ref_period_slider[0] / 100)
                ref_line_end = full_min_date + pd.Timedelta(seconds=total_seconds * ref_period_slider[1] / 100)
            else:
                # Default 10-90%
                ref_line_start = full_min_date + pd.Timedelta(seconds=total_seconds * 0.1)
                ref_line_end = full_min_date + pd.Timedelta(seconds=total_seconds * 0.9)
        
        if df.empty:
            empty_fig.update_layout(title="Žádná data ve vybraném rozsahu")
            return empty_fig, [], "Žádná data ve vybraném časovém rozsahu.", "", ""
        
        df = df.reset_index(drop=True)
        total_points = len(df)
        
        # Calculate tolerance intervals from reference period
        ti_info = ""
        ti_data = {'ti90': None, 'ti95': None, 'ti99': None}
        
        if "datum" in df.columns and ref_line_start is not None and ref_line_end is not None:
            # Filter reference period
            df_ref = df[(df["datum"] >= ref_line_start) & (df["datum"] <= ref_line_end)]
            
            # Exclude MVA values from TI calculation (always, regardless of show_mva setting)
            if "pod_mva" in df_ref.columns:
                df_ref = df_ref[df_ref["pod_mva"] != 1]
            
            if len(df_ref) >= 10 and "hodnota" in df_ref.columns:
                ref_values = df_ref["hodnota"].dropna().values
                ref_values = ref_values[ref_values > 0]
                
                if len(ref_values) >= 10:
                    ti_data = calculate_tolerance_intervals(ref_values)
                    
                    if ti_data['ti99']:
                        start_str = ref_line_start.strftime("%Y-%m") if hasattr(ref_line_start, 'strftime') else str(ref_line_start)[:7]
                        end_str = ref_line_end.strftime("%Y-%m") if hasattr(ref_line_end, 'strftime') else str(ref_line_end)[:7]
                        
                        ti_info = (
                            f"Ref {start_str} – {end_str}: n={ti_data['n']} | "
                            f"TI90={ti_data['ti90']:.3g} | "
                            f"TI95={ti_data['ti95']:.3g} | "
                            f"TI99={ti_data['ti99']:.3g}"
                        )
                        df["is_outlier"] = df["hodnota"] > ti_data['ti99']
        
        # Determine which column to color by based on active filters
        om_filter_active = bool(odber_misto) and (len(odber_misto) > 0 if isinstance(odber_misto, list) else True)
        dod_filter_active = bool(dodavatel) and (len(dodavatel) > 0 if isinstance(dodavatel, list) else True)
        
        # Priority: if both filters active, create combined category; otherwise use the active one
        color_by = None
        if om_filter_active and dod_filter_active:
            # Both filters - create combined category
            if "odber_misto" in df.columns and "dodavatel_dat" in df.columns:
                df["_color_category"] = df["odber_misto"].astype(str) + " | " + df["dodavatel_dat"].astype(str)
                color_by = "_color_category"
        elif om_filter_active:
            color_by = "odber_misto"
        elif dod_filter_active:
            color_by = "dodavatel_dat"
        
        # Build figure
        fig = go.Figure()
        
        if selected_set:
            df["selected"] = df["row_key"].isin(selected_set)
            _add_split_traces(fig, df, color_by=color_by)
        else:
            _add_single_trace(fig, df, color_by=color_by)
        
        # UI revision key for zoom/pan persistence
        # Include y_zoom_mode so Y-axis resets when zoom buttons are clicked
        ui_key = f"{dataset}|{nuklid or ''}|{str(odber_misto) if odber_misto else ''}|{str(dodavatel) if dodavatel else ''}|{y_zoom_mode or ''}"
        
        # Reference period rectangle (semi-transparent green)
        ref_shapes = _build_ref_rectangle(df, ref_line_start, ref_line_end)
        
        # Get jednotka from data if available and unique
        jednotka_label = ""
        if "jednotka" in df.columns and df["jednotka"].nunique() == 1:
            jednotka_label = f" [{df['jednotka'].iloc[0]}]"
        
        # Show legend only if color_by is active and multiple categories exist
        n_categories = df[color_by].nunique() if color_by and color_by in df.columns else 1
        show_legend = color_by is not None and n_categories > 1
        
        # Calculate Y-axis range based on zoom mode
        y_range = None  # None = auto (full range)
        if y_zoom_mode and ti_data and ti_data.get("ti99"):
            ti99 = ti_data["ti99"]
            if y_zoom_mode == "2ti":
                y_range = [0, 2.0 * ti99]
            elif y_zoom_mode == "1ti":
                y_range = [0, 1.05 * ti99]
            # "full" mode keeps y_range = None (auto)
        
        fig.update_layout(
            title=None,
            xaxis_title=None,
            yaxis_title="Hodnota" + jednotka_label,
            yaxis_range=y_range,
            dragmode="select",
            hovermode="closest",
            showlegend=show_legend,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="left",
                x=0,
                font=dict(size=10),
            ) if show_legend else None,
            uirevision=ui_key,
            margin=dict(l=50, r=10, t=40 if show_legend else 10, b=30),
            shapes=ref_shapes,
            # Prevent automatic dimming of unselected points
            newselection=dict(mode="immediate"),
        )
        
        # Apply unselected opacity to all traces to prevent dimming
        fig.update_traces(
            unselected=dict(marker=dict(opacity=_get_opacity_normal())),
            selected=dict(marker=dict(opacity=_get_opacity_normal())),
        )
        
        # TI horizontal lines
        _add_ti_lines(fig, ti_data)
        
        # Outlier markers
        _add_outlier_markers(fig, df)
        
        # Prepare table data
        df_table = df[df["row_key"].isin(selected_set)].copy() if selected_set else df.copy()
        row_data = _prepare_table_data(df_table)
        
        # Info text
        outlier_count = df["is_outlier"].sum() if "is_outlier" in df.columns else 0
        info = f"Vybráno {len(selected_set)} z {total_points} bodů" if selected_set else f"Zobrazeno {total_points} bodů"
        if outlier_count > 0:
            info += f" | {outlier_count} outlierů (> TI99)"
        
        # Table statistics
        table_stats = _calculate_table_stats(df_table)
        
        return fig, row_data, info, ti_info, table_stats


def _parse_datetime_utc(value, fallback):
    """Parse datetime to UTC-aware, with fallback."""
    try:
        if isinstance(value, str):
            return pd.to_datetime(value, utc=True)
        elif hasattr(value, 'tzinfo') and value.tzinfo is None:
            return value.tz_localize('UTC')
        return value
    except:
        return fallback


def _calculate_table_stats(df: pd.DataFrame) -> str:
    """Calculate aggregated statistics for table data."""
    if df.empty or "hodnota" not in df.columns:
        return ""
    
    values = df["hodnota"].dropna()
    if len(values) == 0:
        return ""
    
    n = len(values)
    mean_val = values.mean()
    std_val = values.std() if n > 1 else 0
    min_val = values.min()
    max_val = values.max()
    median_val = values.median()
    
    # Format numbers nicely
    def fmt(x):
        if abs(x) >= 1000:
            return f"{x:.0f}"
        elif abs(x) >= 1:
            return f"{x:.2f}"
        else:
            return f"{x:.3g}"
    
    stats = f"n={n} | průměr={fmt(mean_val)} | medián={fmt(median_val)} | std={fmt(std_val)} | min={fmt(min_val)} | max={fmt(max_val)}"
    return stats


# =============================================================================
# Styling constants (from config)
# =============================================================================

def _get_opacity_normal():
    return config.scatter.opacity_normal

def _get_opacity_selected():
    return config.scatter.opacity_selected

def _get_opacity_dimmed():
    return config.scatter.opacity_dimmed

def _get_marker_size_normal():
    return config.scatter.marker_size_normal

def _get_marker_size_selected():
    return config.scatter.marker_size_selected

def _get_marker_size_highlight():
    return config.scatter.marker_size_highlight

def _get_marker_size_outlier():
    return config.scatter.marker_size_outlier

def _get_default_color():
    return config.scatter.default_color

def _get_selection_color():
    return config.scatter.selection_color

def _get_outlier_color():
    return config.scatter.outlier_color


def _get_color_map(df: pd.DataFrame, color_by: str) -> dict:
    """Create color mapping for categories."""
    if color_by not in df.columns:
        return {}
    categories = df[color_by].dropna().unique()
    colors = config.category_colors
    return {cat: colors[i % len(colors)] for i, cat in enumerate(categories)}


def _add_single_trace(fig: go.Figure, df: pd.DataFrame, color_by: str = None):
    """Add traces for all points, optionally colored by specified column, with MVA as open circles."""
    has_mva = "pod_mva" in df.columns
    
    # Only use multi-color if color_by is specified AND column exists AND multiple categories exist
    n_categories = df[color_by].nunique() if color_by and color_by in df.columns else 1
    use_legend = color_by is not None and n_categories > 1
    
    if not use_legend:
        # Single color mode (no filter active or single category)
        color = _get_default_color()
        _add_category_trace(fig, df, color, None, has_mva, show_legend=False, is_selected=False)
    else:
        # Multiple categories - color by specified column
        color_map = _get_color_map(df, color_by)
        for category, clr in color_map.items():
            df_cat = df[df[color_by] == category]
            if not df_cat.empty:
                _add_category_trace(fig, df_cat, clr, str(category), has_mva, show_legend=True, is_selected=False)


def _add_category_trace(fig: go.Figure, df: pd.DataFrame, color: str, name: str, has_mva: bool, show_legend: bool, is_selected: bool):
    """Add trace(s) for a single category, with MVA as triangles."""
    size = _get_marker_size_selected() if is_selected else _get_marker_size_normal()
    opacity = _get_opacity_selected() if is_selected else _get_opacity_normal()
    
    if has_mva:
        df_mva = df[df["pod_mva"] == 1]
        df_normal = df[df["pod_mva"] != 1]
        
        # Normal points (filled circles)
        if not df_normal.empty:
            fig.add_trace(
                go.Scatter(
                    x=df_normal["datum"] if "datum" in df_normal.columns else df_normal.index,
                    y=df_normal["hodnota"],
                    mode="markers",
                    marker=dict(color=color, size=size, opacity=opacity),
                    customdata=df_normal[["row_key", "odber_misto"]].values if "odber_misto" in df_normal.columns else df_normal[["row_key"]].values,
                    hovertemplate="<b>%{customdata[0]}</b><br>Lokalita: %{customdata[1]}<br>Datum: %{x}<br>Hodnota: %{y}<extra></extra>" if "odber_misto" in df_normal.columns else "<b>%{customdata[0]}</b><br>Datum: %{x}<br>Hodnota: %{y}<extra></extra>",
                    showlegend=show_legend,
                    name=name or "Data",
                    legendgroup=name,
                    unselected=dict(marker=dict(opacity=opacity)),  # Keep same opacity when unselected
                    selected=dict(marker=dict(opacity=opacity)),    # Keep same opacity when selected
                )
            )
        
        # MVA points (open circles)
        if not df_mva.empty:
            fig.add_trace(
                go.Scatter(
                    x=df_mva["datum"] if "datum" in df_mva.columns else df_mva.index,
                    y=df_mva["hodnota"],
                    mode="markers",
                    marker=dict(
                        color=color,
                        size=size,
                        opacity=opacity,
                        symbol="circle-open",
                        line=dict(width=2, color=color),
                    ),
                    customdata=df_mva[["row_key", "odber_misto"]].values if "odber_misto" in df_mva.columns else df_mva[["row_key"]].values,
                    hovertemplate="<b>MVA</b><br>%{customdata[0]}<br>Lokalita: %{customdata[1]}<br>Datum: %{x}<br>Hodnota: %{y}<extra></extra>" if "odber_misto" in df_mva.columns else "<b>MVA</b><br>%{customdata[0]}<br>Datum: %{x}<br>Hodnota: %{y}<extra></extra>",
                    showlegend=False,  # Don't duplicate legend for MVA
                    name=f"{name} (MVA)" if name else "MVA",
                    legendgroup=name,
                    unselected=dict(marker=dict(opacity=opacity)),
                    selected=dict(marker=dict(opacity=opacity)),
                )
            )
    else:
        # No MVA column
        fig.add_trace(
            go.Scatter(
                x=df["datum"] if "datum" in df.columns else df.index,
                y=df["hodnota"],
                mode="markers",
                marker=dict(color=color, size=size, opacity=opacity),
                customdata=df[["row_key", "odber_misto"]].values if "odber_misto" in df.columns else df[["row_key"]].values,
                hovertemplate="<b>%{customdata[0]}</b><br>Lokalita: %{customdata[1]}<br>Datum: %{x}<br>Hodnota: %{y}<extra></extra>" if "odber_misto" in df.columns else "<b>%{customdata[0]}</b><br>Datum: %{x}<br>Hodnota: %{y}<extra></extra>",
                showlegend=show_legend,
                unselected=dict(marker=dict(opacity=opacity)),
                selected=dict(marker=dict(opacity=opacity)),
                name=name or "Data",
                legendgroup=name,
            )
        )


def _add_split_traces(fig: go.Figure, df: pd.DataFrame, color_by: str = None):
    """Add traces with selected points highlighted over the base layer.
    
    Strategy: Draw ALL points normally first, then overlay selected points
    with highlighting. This ensures a fresh-looking graph with selection emphasis.
    """
    df_selected = df[df["selected"]]
    has_mva = "pod_mva" in df.columns
    
    # Only use multi-color if color_by is specified AND column exists AND multiple categories exist
    n_categories = df[color_by].nunique() if color_by and color_by in df.columns else 1
    use_legend = color_by is not None and n_categories > 1
    color_map = _get_color_map(df, color_by) if use_legend else {}
    
    # First: Draw ALL points normally (base layer) - same as _add_single_trace
    if not use_legend:
        color = _get_default_color()
        _add_category_trace(fig, df, color, None, has_mva, show_legend=False, is_selected=False)
    else:
        for category, clr in color_map.items():
            df_cat = df[df[color_by] == category]
            if not df_cat.empty:
                _add_category_trace(fig, df_cat, clr, str(category), has_mva, show_legend=True, is_selected=False)
    
    # Second: Overlay selected points with highlight styling
    if not df_selected.empty:
        _add_selection_highlight(fig, df_selected, has_mva)


def _add_selection_highlight(fig: go.Figure, df: pd.DataFrame, has_mva: bool):
    """Add highlight overlay for selected points - red ring around each point."""
    selection_color = _get_selection_color()
    highlight_size = _get_marker_size_highlight()
    
    fig.add_trace(
        go.Scatter(
            x=df["datum"] if "datum" in df.columns else df.index,
            y=df["hodnota"],
            mode="markers",
            marker=dict(
                color=selection_color,
                size=highlight_size,
                opacity=1.0,
                symbol="circle-open",
                line=dict(width=2.5, color=selection_color),
            ),
            customdata=df[["row_key"]].values,
            hovertemplate="<b>VYBRÁNO</b><br>%{customdata[0]}<br>Datum: %{x}<br>Hodnota: %{y}<extra></extra>",
            showlegend=False,
            name="Vybrané",
        )
    )


# Keep _add_unselected_category_trace for potential future use but it's not used now
def _add_unselected_category_trace(fig: go.Figure, df: pd.DataFrame, color: str, name: str, has_mva: bool):
    """Add dimmed trace for unselected points (currently unused)."""
    # Make color lighter/more transparent for unselected
    size = _get_marker_size_normal() - 2  # Slightly smaller than normal
    opacity_dimmed = _get_opacity_dimmed()
    
    if has_mva:
        df_mva = df[df["pod_mva"] == 1]
        df_normal = df[df["pod_mva"] != 1]
        
        if not df_normal.empty:
            fig.add_trace(
                go.Scatter(
                    x=df_normal["datum"] if "datum" in df_normal.columns else df_normal.index,
                    y=df_normal["hodnota"],
                    mode="markers",
                    marker=dict(color=color, size=size, opacity=opacity_dimmed),
                    customdata=df_normal[["row_key"]].values,
                    hovertemplate="<b>%{customdata[0]}</b><br>Datum: %{x}<br>Hodnota: %{y}<extra></extra>",
                    showlegend=False,
                    legendgroup=name,
                )
            )
        
        # MVA as open circles
        if not df_mva.empty:
            fig.add_trace(
                go.Scatter(
                    x=df_mva["datum"] if "datum" in df_mva.columns else df_mva.index,
                    y=df_mva["hodnota"],
                    mode="markers",
                    marker=dict(color=color, size=size, opacity=opacity_dimmed, symbol="circle-open", line=dict(width=1.5, color=color)),
                    customdata=df_mva[["row_key"]].values,
                    hovertemplate="<b>MVA</b><br>%{customdata[0]}<br>Datum: %{x}<br>Hodnota: %{y}<extra></extra>",
                    showlegend=False,
                    legendgroup=name,
                )
            )
    else:
        fig.add_trace(
            go.Scatter(
                x=df["datum"] if "datum" in df.columns else df.index,
                y=df["hodnota"],
                mode="markers",
                marker=dict(color=color, size=size, opacity=opacity_dimmed),
                customdata=df[["row_key"]].values,
                hovertemplate="<b>%{customdata[0]}</b><br>Datum: %{x}<br>Hodnota: %{y}<extra></extra>",
                showlegend=False,
                legendgroup=name,
            )
        )


def _build_ref_rectangle(df: pd.DataFrame, start, end) -> list:
    """Build semi-transparent rectangle for reference period."""
    if "datum" not in df.columns or start is None or end is None:
        return []
    
    return [
        dict(
            type="rect",
            x0=start,
            x1=end,
            y0=0,
            y1=1,
            yref="paper",
            fillcolor=config.scatter.reference_fill_color,
            line=dict(width=0),  # No border
            layer="below",  # Draw behind data points
        ),
    ]


def _add_ti_lines(fig: go.Figure, ti_data: dict):
    """Add horizontal tolerance interval lines."""
    if ti_data['ti90']:
        fig.add_hline(y=ti_data['ti90'], line_dash="dash", line_color=config.scatter.ti90_color,
                      line_width=1, annotation_text="TI90", annotation_position="right",
                      layer="above")
    if ti_data['ti95']:
        fig.add_hline(y=ti_data['ti95'], line_dash="dash", line_color=config.scatter.ti95_color,
                      line_width=1, annotation_text="TI95", annotation_position="right",
                      layer="above")
    if ti_data['ti99']:
        fig.add_hline(y=ti_data['ti99'], line_dash="dash", line_color=config.scatter.ti99_color,
                      line_width=1, annotation_text="TI99", annotation_position="right",
                      layer="above")


def _add_outlier_markers(fig: go.Figure, df: pd.DataFrame):
    """Add outlier point markers (circles around outliers)."""
    if "is_outlier" not in df.columns:
        return
    
    df_outliers = df[df["is_outlier"] == True]
    if df_outliers.empty:
        return
    
    outlier_color = _get_outlier_color()
    outlier_size = _get_marker_size_outlier()
    
    fig.add_trace(
        go.Scatter(
            x=df_outliers["datum"] if "datum" in df_outliers.columns else df_outliers.index,
            y=df_outliers["hodnota"],
            mode="markers",
            marker=dict(
                color=outlier_color, size=outlier_size, opacity=1.0,
                symbol="circle-open", line=dict(width=2, color=outlier_color),
            ),
            customdata=df_outliers[["row_key"]].values,
            hovertemplate="<b>OUTLIER</b><br>%{customdata[0]}<br>Datum: %{x}<br>Hodnota: %{y}<extra></extra>",
            showlegend=False,
        )
    )


def _prepare_table_data(df: pd.DataFrame) -> list:
    """Prepare DataFrame for AG Grid."""
    cols = [
        "row_key", "datum_display", "hodnota", "nejistota", "pod_mva",
        "nuklid", "jednotka", "odber_misto", "dodavatel_dat", "id_zppr_vzorek"
    ]
    available = [c for c in cols if c in df.columns]
    df_out = df[available].copy()
    if "datum_display" in df_out.columns:
        df_out = df_out.rename(columns={"datum_display": "datum"})
    return df_out.to_dict("records")
