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
