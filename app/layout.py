"""
Layout definition for MRS Viewer MVP.

Defines the UI structure: sidebar with filters + main area with scatter plot and table.
"""
import dash_ag_grid as dag
import dash_bootstrap_components as dbc
from dash import dcc, html

from . import ids
from .data.cache import get_cached_tables


def create_sidebar() -> dbc.Card:
    """Create the sidebar with filter dropdowns and reference period controls."""
    
    # Get initial table list from cache
    try:
        tables = get_cached_tables()
    except FileNotFoundError:
        tables = []
    
    return dbc.Card(
        [
            dbc.CardHeader(html.H5("Filtry", className="mb-0")),
            dbc.CardBody(
                [
                    # Dataset dropdown
                    dbc.Label("Dataset (tabulka)"),
                    dcc.Dropdown(
                        id=ids.DROPDOWN_DATASET,
                        options=[{"label": t, "value": t} for t in tables],
                        value=tables[0] if tables else None,
                        placeholder="Vyberte dataset...",
                        clearable=False,
                    ),
                    html.Hr(),
                    
                    # Nuklid dropdown
                    dbc.Label("Nuklid"),
                    dcc.Dropdown(
                        id=ids.DROPDOWN_NUKLID,
                        placeholder="Všechny nuklidy",
                        clearable=True,
                    ),
                    html.Br(),
                    
                    # Odběrové místo dropdown (multi-select)
                    dbc.Label("Odběrové místo"),
                    dcc.Dropdown(
                        id=ids.DROPDOWN_OM,
                        placeholder="Všechna místa",
                        clearable=True,
                        multi=True,
                    ),
                    html.Br(),
                    
                    # Dodavatel dropdown (multi-select)
                    dbc.Label("Dodavatel dat"),
                    dcc.Dropdown(
                        id=ids.DROPDOWN_DODAVATEL,
                        placeholder="Všichni dodavatelé",
                        clearable=True,
                        multi=True,
                    ),
                    html.Hr(),
                    
                    # Data range slider section
                    dbc.Label("Rozsah dat v grafu", className="fw-bold"),
                    html.Div(id="data-range-dates", className="text-muted small mb-1"),
                    dcc.RangeSlider(
                        id=ids.SLIDER_DATA_RANGE,
                        min=0,
                        max=100,
                        value=[0, 100],
                        marks=None,
                        tooltip={"placement": "bottom", "always_visible": False},
                        allowCross=False,
                    ),
                    html.Br(),
                    
                    # Reference period slider section
                    dbc.Label("Referenční období (pro TI)", className="fw-bold"),
                    html.Div(id="ref-period-dates", className="text-muted small mb-1"),
                    dcc.RangeSlider(
                        id=ids.SLIDER_REF_PERIOD,
                        min=0,
                        max=100,
                        value=[10, 90],
                        marks=None,
                        tooltip={"placement": "bottom", "always_visible": False},
                        allowCross=False,
                    ),
                    
                    html.Hr(),
                    
                    # Y-axis zoom buttons
                    dbc.Label("Zoom osy Y", className="fw-bold"),
                    dbc.ButtonGroup(
                        [
                            dbc.Button("2×TI99", id=ids.BTN_ZOOM_2TI, color="primary", outline=True, size="sm"),
                            dbc.Button("1×TI99", id=ids.BTN_ZOOM_1TI, color="primary", outline=True, size="sm"),
                            dbc.Button("Vše", id=ids.BTN_ZOOM_FULL, color="primary", outline=True, size="sm"),
                        ],
                        className="w-100 mb-2",
                    ),
                    # Store for Y zoom mode
                    dcc.Store(id=ids.STORE_Y_ZOOM, data="2ti"),  # Default: 2*TI99
                    
                    html.Hr(),
                    
                    # Reset button
                    dbc.Button(
                        "Reset výběru",
                        id=ids.BTN_RESET,
                        color="secondary",
                        outline=True,
                        className="w-100",
                    ),
                ]
            ),
        ],
        className="h-100",
    )


def create_scatter_plot() -> dcc.Graph:
    """Create the scatter plot component."""
    return dcc.Graph(
        id=ids.SCATTER_PLOT,
        config={
            "displayModeBar": True,
            "modeBarButtonsToAdd": ["select2d", "lasso2d"],
            "scrollZoom": True,
        },
        style={"height": "420px"},
    )


def create_data_table() -> dag.AgGrid:
    """Create the AG Grid table component."""
    column_defs = [
        {"field": "datum", "headerName": "Datum", "sortable": True, "filter": True},
        {"field": "hodnota", "headerName": "Hodnota", "sortable": True, "filter": "agNumberColumnFilter"},
        {"field": "nejistota", "headerName": "Nejistota", "sortable": True, "filter": "agNumberColumnFilter"},
        {"field": "pod_mva", "headerName": "MVA", "sortable": True, "filter": True},
        {"field": "nuklid", "headerName": "Nuklid", "sortable": True, "filter": True},
        {"field": "jednotka", "headerName": "Jednotka", "sortable": True, "filter": True},
        {"field": "odber_misto", "headerName": "Odběrové místo", "sortable": True, "filter": True},
        {"field": "dodavatel_dat", "headerName": "Dodavatel", "sortable": True, "filter": True},
        {"field": "id_zppr_vzorek", "headerName": "ID Vzorek", "sortable": True, "filter": True},
    ]
    
    return dag.AgGrid(
        id=ids.AGGRID_TABLE,
        columnDefs=column_defs,
        rowData=[],
        defaultColDef={
            "resizable": True,
            "minWidth": 100,
        },
        dashGridOptions={
            "pagination": True,
            "paginationPageSize": 50,
            "rowSelection": "multiple",
        },
        getRowId="params.data.row_key",
        style={"height": "400px"},
        className="ag-theme-alpine",
    )


def create_layout() -> dbc.Container:
    """Create the main application layout."""
    return dbc.Container(
        [
            # Hidden stores
            dcc.Store(id=ids.STORE_SELECTION, data=[]),
            dcc.Store(id=ids.STORE_DATE_RANGE, data={"min": None, "max": None}),
            
            # Header
            dbc.Row(
                dbc.Col(
                    html.H2("MRS Viewer", className="text-primary my-3"),
                    width=12,
                ),
            ),
            
            # Main content
            dbc.Row(
                [
                    # Sidebar
                    dbc.Col(
                        create_sidebar(),
                        width=3,
                    ),
                    
                    # Main area
                    dbc.Col(
                        [
                            # Info text
                            html.Div(
                                id=ids.INFO_TEXT,
                                className="mb-2 text-muted",
                            ),
                            
                            # Scatter plot
                            dbc.Card(
                                [
                                    dbc.CardHeader([
                                        "Scatter Plot",
                                        html.Span(
                                            id=ids.TI_INFO,
                                            className="ms-3 text-muted small",
                                        ),
                                    ]),
                                    dbc.CardBody([
                                        create_scatter_plot(),
                                    ]),
                                ],
                                className="mb-3",
                            ),
                            
                            # Data table
                            dbc.Card(
                                [
                                    dbc.CardHeader("Data"),
                                    dbc.CardBody(create_data_table()),
                                ],
                            ),
                        ],
                        width=9,
                    ),
                ],
            ),
        ],
        fluid=True,
        className="py-3",
    )
