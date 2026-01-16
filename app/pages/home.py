"""
Home page - Main MRS Viewer dashboard.
"""
import dash_ag_grid as dag
import dash_bootstrap_components as dbc
from dash import dcc, html

from .. import ids
from ..config import config


def create_sidebar() -> dbc.Card:
    """Create the sidebar with filter dropdowns and reference period controls."""
    from ..data.cache import get_cached_tables
    
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
                        value=None,
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
                        step=0.5,
                        value=[0, 100],
                        marks=None,
                        tooltip={
                            "placement": "bottom",
                            "always_visible": False,
                            "transform": "dataRangeTooltip",
                        },
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
                        step=0.5,
                        value=[10, 90],
                        marks=None,
                        tooltip={
                            "placement": "bottom",
                            "always_visible": False,
                            "transform": "refPeriodTooltip",
                        },
                        allowCross=False,
                    ),
                    
                    html.Hr(),
                    
                    # Histogram bins slider
                    dbc.Label("Počet binů histogramu", className="fw-bold"),
                    html.Div(id="histogram-bins-value", className="text-muted small mb-1"),
                    dcc.Slider(
                        id=ids.SLIDER_HISTOGRAM_BINS,
                        min=config.histogram.min_bins,
                        max=config.histogram.max_bins,
                        step=config.histogram.bin_step,
                        value=config.histogram.default_bins,
                        marks=None,
                        tooltip={"placement": "bottom", "always_visible": False},
                    ),
                    
                    html.Hr(),
                    
                    # MVA toggle
                    dbc.Label("Zobrazení MVA", className="fw-bold"),
                    dbc.Button(
                        "MVA: Zobrazeno",
                        id=ids.BTN_SHOW_MVA,
                        color="success",
                        outline=True,
                        size="sm",
                        active=True,
                        className="w-100 mb-2",
                    ),
                    dcc.Store(id=ids.STORE_SHOW_MVA, data=True),  # Default: show MVA
                    
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
        style={"height": f"{config.layout.scatter_height}px"},
    )


def create_data_table() -> dag.AgGrid:
    """Create the AG Grid table component with row selection."""
    column_defs = [
        {
            "field": "checkbox",
            "headerName": "",
            "checkboxSelection": True,
            "headerCheckboxSelection": True,
            "width": 50,
            "maxWidth": 50,
            "sortable": False,
            "filter": False,
            "resizable": False,
            "pinned": "left",
        },
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
            "minWidth": config.table.min_column_width,
        },
        dashGridOptions={
            "pagination": True,
            "paginationPageSize": config.table.page_size,
            "rowSelection": "multiple",
            "suppressRowClickSelection": True,
        },
        getRowId="params.data.row_key",
        style={"height": f"{config.layout.table_height}px"},
        className="ag-theme-alpine",
    )


def create_suspicious_table() -> dag.AgGrid:
    """Create the AG Grid table for suspicious records basket."""
    column_defs = [
        {
            "field": "checkbox",
            "headerName": "",
            "checkboxSelection": True,
            "headerCheckboxSelection": True,
            "width": 50,
            "maxWidth": 50,
            "sortable": False,
            "filter": False,
            "resizable": False,
            "pinned": "left",
        },
        {"field": "dataset", "headerName": "Dataset", "sortable": True, "filter": True, "width": 120},
        {"field": "nuklid", "headerName": "Nuklid", "sortable": True, "filter": True, "width": 100},
        {"field": "datum", "headerName": "Datum", "sortable": True, "filter": True, "width": 110},
        {"field": "hodnota", "headerName": "Hodnota", "sortable": True, "filter": "agNumberColumnFilter", "width": 100},
        {"field": "nejistota", "headerName": "Nejistota", "sortable": True, "filter": "agNumberColumnFilter", "width": 100},
        {"field": "jednotka", "headerName": "Jednotka", "sortable": True, "filter": True, "width": 90},
        {"field": "odber_misto", "headerName": "Odběrové místo", "sortable": True, "filter": True, "width": 150},
        {"field": "dodavatel_dat", "headerName": "Dodavatel", "sortable": True, "filter": True, "width": 120},
        {"field": "id_zppr_vzorek", "headerName": "ID Vzorek", "sortable": True, "filter": True, "width": 120},
    ]
    
    return dag.AgGrid(
        id=ids.AGGRID_SUSPICIOUS,
        columnDefs=column_defs,
        rowData=[],
        defaultColDef={
            "resizable": True,
        },
        dashGridOptions={
            "pagination": True,
            "paginationPageSize": 20,
            "rowSelection": "multiple",
            "suppressRowClickSelection": True,
        },
        getRowId="params.data.row_key",
        style={"height": "250px"},
        className="ag-theme-alpine",
    )


def create_home_page() -> dbc.Container:
    """Create the home page content (main dashboard)."""
    return dbc.Container(
        [
            # Hidden stores
            dcc.Store(id=ids.STORE_SELECTION, data=[]),
            dcc.Store(id=ids.STORE_DATE_RANGE, data={"min": None, "max": None}),
            
            # Dummy div for clientside callback (syncs date range to JS)
            html.Div(id=ids.DUMMY_DATE_RANGE_SYNC, style={"display": "none"}),
            
            # Main content
            dbc.Row(
                [
                    # Sidebar
                    dbc.Col(
                        create_sidebar(),
                        width=config.layout.sidebar_width,
                    ),
                    
                    # Main area
                    dbc.Col(
                        [
                            # Scatter plot row
                            dbc.Row(
                                [
                                    dbc.Col(
                                        dbc.Card(
                                            [
                                                dbc.CardHeader(
                                                    dbc.Row(
                                                        [
                                                            dbc.Col(
                                                                [
                                                                    html.Span(
                                                                        id=ids.INFO_TEXT,
                                                                        className="me-3",
                                                                    ),
                                                                    html.Span(
                                                                        id=ids.TI_INFO,
                                                                        className="text-muted small",
                                                                    ),
                                                                ],
                                                            ),
                                                            dbc.Col(
                                                                dbc.ButtonGroup(
                                                                    [
                                                                        dbc.Button("2×TI99", id=ids.BTN_ZOOM_2TI, color="primary", outline=True, size="sm", active=True),
                                                                        dbc.Button("1×TI99", id=ids.BTN_ZOOM_1TI, color="primary", outline=True, size="sm"),
                                                                        dbc.Button("Vše", id=ids.BTN_ZOOM_FULL, color="primary", outline=True, size="sm"),
                                                                    ],
                                                                ),
                                                                width="auto",
                                                            ),
                                                        ],
                                                        className="align-items-center",
                                                    ),
                                                ),
                                                # Store for Y zoom mode
                                                dcc.Store(id=ids.STORE_Y_ZOOM, data="2ti"),
                                                dbc.CardBody([
                                                    create_scatter_plot(),
                                                ], className="p-2"),
                                            ],
                                            className="h-100",
                                        ),
                                        width=config.layout.left_chart_width,
                                    ),
                                    dbc.Col(
                                        dbc.Card(
                                            [
                                                dbc.CardHeader([
                                                    dbc.ButtonGroup(
                                                        [
                                                            dbc.Button(
                                                                "Místo",
                                                                id=ids.BTN_BOXPLOT_BY_OM,
                                                                color="primary",
                                                                outline=True,
                                                                size="sm",
                                                                active=True,
                                                            ),
                                                            dbc.Button(
                                                                "Dodavatel",
                                                                id=ids.BTN_BOXPLOT_BY_DODAVATEL,
                                                                color="primary",
                                                                outline=True,
                                                                size="sm",
                                                            ),
                                                        ],
                                                        size="sm",
                                                    ),
                                                    dbc.Button(
                                                        "Outliers",
                                                        id=ids.BTN_BOXPLOT_OUTLIERS,
                                                        color="secondary",
                                                        outline=True,
                                                        size="sm",
                                                        active=True,
                                                        className="ms-2",
                                                    ),
                                                ]),
                                                dbc.CardBody([
                                                    dcc.Store(id=ids.STORE_BOXPLOT_MODE, data="om"),
                                                    dcc.Store(id=ids.STORE_BOXPLOT_OUTLIERS, data=True),
                                                    dcc.Graph(
                                                        id=ids.CHART_SIDE_TOP,
                                                        style={"height": f"{config.layout.boxplot_height}px"},
                                                        config={"displayModeBar": False},
                                                    ),
                                                ], className="p-2"),
                                            ],
                                            className="h-100",
                                        ),
                                        width=config.layout.right_chart_width,
                                    ),
                                ],
                                className="mb-3",
                            ),
                            
                            # Data table row
                            dbc.Row(
                                [
                                    dbc.Col(
                                        dbc.Card(
                                            [
                                                dbc.CardHeader(
                                                    dbc.Row(
                                                        [
                                                            dbc.Col(
                                                                html.Span(id=ids.TABLE_STATS, className="small"),
                                                            ),
                                                            dbc.Col(
                                                                dbc.Button(
                                                                    [html.I(className="bi bi-plus-circle me-1"), "Přidat do zásobníku"],
                                                                    id=ids.BTN_ADD_TO_SUSPICIOUS,
                                                                    color="warning",
                                                                    size="sm",
                                                                    outline=True,
                                                                ),
                                                                width="auto",
                                                            ),
                                                        ],
                                                        className="align-items-center",
                                                    ),
                                                    className="py-2",
                                                ),
                                                dbc.CardBody(create_data_table(), className="p-2"),
                                            ],
                                            className="h-100",
                                        ),
                                        width=config.layout.left_chart_width,
                                    ),
                                    dbc.Col(
                                        dbc.Card(
                                            [
                                                dbc.CardHeader(
                                                    "Histogram",
                                                    className="py-2",
                                                ),
                                                dbc.CardBody([
                                                    dcc.Graph(
                                                        id=ids.CHART_SIDE_BOTTOM,
                                                        style={"height": f"{config.layout.histogram_height}px"},
                                                        config={"displayModeBar": False},
                                                    ),
                                                ], className="p-2"),
                                            ],
                                            className="h-100",
                                        ),
                                        width=config.layout.right_chart_width,
                                    ),
                                ],
                                className="mb-3",
                            ),
                            
                            # Suspicious records basket row
                            dbc.Row(
                                [
                                    dbc.Col(
                                        dbc.Card(
                                            [
                                                dbc.CardHeader(
                                                    dbc.Row(
                                                        [
                                                            dbc.Col(
                                                                [
                                                                    html.I(className="bi bi-exclamation-triangle text-warning me-2"),
                                                                    "Zásobník podezřelých záznamů ",
                                                                    dbc.Badge(
                                                                        "0",
                                                                        id=ids.SUSPICIOUS_COUNT_BADGE,
                                                                        color="warning",
                                                                        pill=True,
                                                                        className="ms-1",
                                                                    ),
                                                                ],
                                                            ),
                                                            dbc.Col(
                                                                dbc.ButtonGroup(
                                                                    [
                                                                        dbc.Button(
                                                                            [html.I(className="bi bi-file-earmark-excel me-1"), "Export"],
                                                                            id=ids.BTN_EXPORT_SUSPICIOUS,
                                                                            color="success",
                                                                            size="sm",
                                                                            outline=True,
                                                                        ),
                                                                        dbc.Button(
                                                                            [html.I(className="bi bi-trash me-1"), "Odebrat vybrané"],
                                                                            id=ids.BTN_CLEAR_SUSPICIOUS,
                                                                            color="danger",
                                                                            size="sm",
                                                                            outline=True,
                                                                        ),
                                                                    ],
                                                                    size="sm",
                                                                ),
                                                                width="auto",
                                                            ),
                                                        ],
                                                        className="align-items-center",
                                                    ),
                                                    className="py-2",
                                                ),
                                                dbc.CardBody(create_suspicious_table(), className="p-2"),
                                            ],
                                        ),
                                        width=config.layout.left_chart_width,
                                    ),
                                    dbc.Col(
                                        dbc.Card(
                                            [
                                                dbc.CardHeader(
                                                    dbc.Row(
                                                        [
                                                            dbc.Col(
                                                                [
                                                                    html.I(className="bi bi-journal-text me-2"),
                                                                    "Log aktivit",
                                                                ],
                                                            ),
                                                            dbc.Col(
                                                                dbc.Button(
                                                                    [html.I(className="bi bi-trash me-1"), "Vymazat"],
                                                                    id=ids.BTN_CLEAR_STATUS_LOG,
                                                                    color="secondary",
                                                                    size="sm",
                                                                    outline=True,
                                                                ),
                                                                width="auto",
                                                            ),
                                                        ],
                                                        className="align-items-center",
                                                    ),
                                                    className="py-2",
                                                ),
                                                dbc.CardBody(
                                                    html.Div(
                                                        id=ids.STATUS_LOG_CONTAINER,
                                                        style={
                                                            "height": "220px",
                                                            "overflowY": "auto",
                                                        },
                                                    ),
                                                    className="p-2",
                                                ),
                                            ],
                                        ),
                                        width=config.layout.right_chart_width,
                                    ),
                                ],
                            ),
                        ],
                        width=config.layout.main_area_width,
                    ),
                ],
            ),
            
            # Session store for suspicious records (persists during navigation, clears on reload)
            dcc.Store(id=ids.STORE_SUSPICIOUS, storage_type="memory", data={"records": []}),
            
            # Session store for status log (persists during navigation, clears on reload)
            dcc.Store(id=ids.STORE_STATUS_LOG, storage_type="memory", data={"entries": []}),
            
            # Download component for Excel export
            dcc.Download(id=ids.DOWNLOAD_SUSPICIOUS),
            
            # Toast container for notifications
            html.Div(id=ids.TOAST_CONTAINER),
        ],
        fluid=True,
    )
