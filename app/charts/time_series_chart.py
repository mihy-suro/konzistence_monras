"""
Časové řady.

Funkce pro vizualizaci dat v čase:
- Vývoj hodnot v čase
- Agregace podle měsíců/roků
- Trend s confidence intervalem

Časové grafy používají interaktivní zoom a pan.
"""

import altair as alt
import pandas as pd
from typing import Optional


def create_time_series_chart(
    df: pd.DataFrame,
    date_column: str,
    value_column: str,
    color_column: Optional[str] = None,
    aggregate: Optional[str] = None,
) -> alt.Chart:
    """
    Vytvoří časovou řadu z dat.
    
    Args:
        df: DataFrame s daty
        date_column: Název sloupce s datem
        value_column: Název sloupce s hodnotou
        color_column: Volitelný sloupec pro barvu čar
        aggregate: Agregační funkce ("mean", "sum", "count")
        
    Returns:
        alt.Chart časová řada
    """
    # TODO: Implementovat time series chart
    chart = alt.Chart(df).mark_line().encode(
        x=date_column,
        y=value_column,
    )
    
    if color_column:
        chart = chart.encode(color=color_column)
    
    return chart.interactive()
