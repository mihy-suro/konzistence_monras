"""
Bodové grafy (scatter plots).

Funkce pro vytváření scatter plotů z MonRaS dat:
- Hodnota vs Nejistota
- Geografická vizualizace (lon/lat)
- Časová závislost hodnot

Podporuje selection pro crossfiltering s ostatními grafy.
"""

import altair as alt
import pandas as pd
from typing import Optional


def create_scatter_chart(
    df: pd.DataFrame,
    x_column: str,
    y_column: str,
    color_column: Optional[str] = None,
    selection: Optional[alt.Parameter] = None,
) -> alt.Chart:
    """
    Vytvoří scatter plot z dat.
    
    Args:
        df: DataFrame s daty
        x_column: Název sloupce pro osu X
        y_column: Název sloupce pro osu Y
        color_column: Volitelný sloupec pro barvu bodů
        selection: Volitelná selekce pro crossfiltering
        
    Returns:
        alt.Chart scatter plot
    """
    # TODO: Implementovat scatter chart
    chart = alt.Chart(df).mark_circle().encode(
        x=x_column,
        y=y_column,
    )
    
    if color_column:
        chart = chart.encode(color=color_column)
    
    if selection:
        chart = chart.add_params(selection)
    
    return chart
