"""
Component IDs for MRS Viewer MVP.

Centralized ID constants to avoid typos and enable easy refactoring.
"""

# Sidebar - Filter dropdowns
DROPDOWN_DATASET = "dropdown-dataset"
DROPDOWN_NUKLID = "dropdown-nuklid"
DROPDOWN_OM = "dropdown-om"  # Multi-select
DROPDOWN_DODAVATEL = "dropdown-dodavatel"  # Multi-select

# Buttons
BTN_RESET = "btn-reset"

# Main content
SCATTER_PLOT = "scatter-plot"
AGGRID_TABLE = "aggrid-table"

# Info display
INFO_TEXT = "info-text"
TABLE_STATS = "table-stats"  # Aggregated statistics for data table

# Data stores
STORE_DATA = "store-data"
STORE_SELECTION = "store-selection"

# Tolerance intervals
TI_INFO = "ti-info"

# Range sliders
SLIDER_DATA_RANGE = "slider-data-range"  # Controls visible data range
SLIDER_REF_PERIOD = "slider-ref-period"  # Controls reference period for TI
STORE_DATE_RANGE = "store-date-range"  # Stores min/max dates from data

# Y-axis zoom buttons
BTN_ZOOM_2TI = "btn-zoom-2ti"      # 0 - 2*TI99
BTN_ZOOM_1TI = "btn-zoom-1ti"      # 0 - 1.05*TI99
BTN_ZOOM_FULL = "btn-zoom-full"    # Full range
STORE_Y_ZOOM = "store-y-zoom"      # Stores current zoom mode

# MVA toggle
BTN_SHOW_MVA = "btn-show-mva"       # Toggle MVA visibility
STORE_SHOW_MVA = "store-show-mva"   # Stores MVA visibility: True/False

# Interactive side charts
CHART_SIDE_TOP = "chart-side-top"       # Chart next to scatter plot
CHART_SIDE_BOTTOM = "chart-side-bottom"  # Chart next to data table

# Boxplot controls
BTN_BOXPLOT_BY_OM = "btn-boxplot-by-om"           # Group by location
BTN_BOXPLOT_BY_DODAVATEL = "btn-boxplot-by-dodavatel"  # Group by supplier
STORE_BOXPLOT_MODE = "store-boxplot-mode"         # Stores grouping mode: "om" or "dodavatel"
BTN_BOXPLOT_OUTLIERS = "btn-boxplot-outliers"     # Toggle outliers visibility
STORE_BOXPLOT_OUTLIERS = "store-boxplot-outliers" # Stores outliers visibility: True/False

# Histogram controls
SLIDER_HISTOGRAM_BINS = "slider-histogram-bins"  # Number of bins in histogram

# Dummy elements for clientside callbacks
DUMMY_DATE_RANGE_SYNC = "dummy-date-range-sync"  # For syncing date range to JS

# Routing
URL_LOCATION = "url-location"  # URL location for routing
PAGE_CONTENT = "page-content"  # Container for page content

# Config editor page
BTN_CONFIG_SAVE = "btn-config-save"
BTN_CONFIG_RELOAD = "btn-config-reload"
CONFIG_EDITOR = "config-editor"
CONFIG_STATUS = "config-status"
STORE_CONFIG_LOADED = "store-config-loaded"

# Suspicious records basket
AGGRID_SUSPICIOUS = "aggrid-suspicious"           # AG Grid for suspicious records
BTN_ADD_TO_SUSPICIOUS = "btn-add-to-suspicious"   # Add selected rows to basket
BTN_CLEAR_SUSPICIOUS = "btn-clear-suspicious"     # Clear entire basket
BTN_EXPORT_SUSPICIOUS = "btn-export-suspicious"   # Export to Excel
STORE_SUSPICIOUS = "store-suspicious"             # Session store for records
DOWNLOAD_SUSPICIOUS = "download-suspicious"       # Download component
SUSPICIOUS_COUNT_BADGE = "suspicious-count-badge" # Badge showing count
TOAST_CONTAINER = "toast-container"               # Container for toast notifications

# Status log panel
STATUS_LOG_CONTAINER = "status-log-container"     # Container for log entries
STORE_STATUS_LOG = "store-status-log"             # Session store for log entries
BTN_CLEAR_STATUS_LOG = "btn-clear-status-log"     # Clear log button
