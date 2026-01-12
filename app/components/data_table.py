"""
Komponenta pro zobrazení dat v tabulce.

Využívá dash-ag-grid pro:
- Stránkování velkých datasetů
- Třídění podle sloupců
- Filtrování v rámci tabulky
- Výběr řádků
- Export dat

Tabulka je responzivní a podporuje velké množství dat.
"""

import dash_ag_grid as dag
import dash_bootstrap_components as dbc


def create_data_table(
    component_id: str = "data-table",
    page_size: int = 25,
) -> dag.AgGrid:
    """
    Vytvoří AG Grid tabulku pro zobrazení dat.
    
    Args:
        component_id: ID komponenty pro callbacks
        page_size: Počet řádků na stránku
        
    Returns:
        dag.AgGrid komponenta
    """
    # TODO: Implementovat data table
    return dag.AgGrid(
        id=component_id,
        rowData=[],
        columnDefs=[],
        defaultColDef={
            "filter": True,
            "sortable": True,
            "resizable": True,
        },
        dashGridOptions={
            "pagination": True,
            "paginationPageSize": page_size,
        },
        style={"height": "500px"},
    )
