"""
Histogramy a distribuce.

Funkce pro vytváření histogramů a vizualizací distribucí:
- Histogram hodnot
- Distribuce nejistot
- Počet měření v čase

Histogramy reagují na crossfilter selekci - zobrazují
pouze vybrané body.
"""

import altair as alt
import pandas as pd
from typing import Optional


def create_histogram_chart(
    df: pd.DataFrame,
    column: str,
    bin_count: int = 30,
    selection: Optional[alt.Parameter] = None,
) -> alt.Chart:
    """
    Vytvoří histogram ze sloupce dat.
    
    Args:
        df: DataFrame s daty
        column: Název sloupce pro histogram
        bin_count: Počet binů
        selection: Volitelná selekce pro crossfiltering
        
    Returns:
        alt.Chart histogram
    """
    # TODO: Implementovat histogram chart
    chart = alt.Chart(df).mark_bar().encode(
        x=alt.X(column, bin=alt.Bin(maxbins=bin_count)),
        y="count()",
    )
    
    if selection:
        chart = chart.transform_filter(selection)
    
    return chart
