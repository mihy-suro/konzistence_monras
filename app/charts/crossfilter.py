"""
Utility pro crossfiltering mezi grafy.

Crossfiltering umožňuje:
- Výběr bodů v jednom grafu filtruje ostatní
- Brush selection (obdélníkový výběr)
- Point selection (kliknutí na bod)
- Multi-select s Shift

Sdílené selection objekty propojují všechny grafy.
"""

import altair as alt
import pandas as pd
from typing import Optional


def create_brush_selection(name: str = "brush") -> alt.Parameter:
    """
    Vytvoří brush selection pro crossfiltering.
    
    Args:
        name: Název selekce pro reference
        
    Returns:
        alt.Parameter interval selection
    """
    return alt.selection_interval(name=name)


def create_point_selection(name: str = "point") -> alt.Parameter:
    """
    Vytvoří point selection pro crossfiltering.
    
    Args:
        name: Název selekce pro reference
        
    Returns:
        alt.Parameter point selection
    """
    return alt.selection_point(name=name)


def create_crossfilter_charts(
    df: pd.DataFrame,
    x_column: str = "Hodnota",
    y_column: str = "Nejistota",
    color_column: Optional[str] = None,
) -> alt.VConcatChart:
    """
    Vytvoří sadu propojených grafů s crossfilteringem.
    
    Vrací:
    - Scatter plot (hlavní)
    - Histogram X hodnot
    - Histogram Y hodnot
    
    Výběr ve scatter plotu filtruje oba histogramy.
    
    Args:
        df: DataFrame s daty
        x_column: Sloupec pro X osu scatter plotu
        y_column: Sloupec pro Y osu scatter plotu
        color_column: Sloupec pro barvu bodů
        
    Returns:
        alt.VConcatChart s propojenými grafy
    """
    # TODO: Implementovat crossfilter charts
    brush = create_brush_selection()
    
    # Scatter plot s brush selection
    scatter = alt.Chart(df).mark_circle().encode(
        x=f"{x_column}:Q",
        y=f"{y_column}:Q",
        color=alt.condition(brush, alt.value("steelblue"), alt.value("lightgray")),
    ).add_params(brush)
    
    # Histogramy filtrované brush selekcí
    hist_x = alt.Chart(df).mark_bar().encode(
        x=alt.X(f"{x_column}:Q", bin=True),
        y="count()",
    ).transform_filter(brush)
    
    hist_y = alt.Chart(df).mark_bar().encode(
        x=alt.X(f"{y_column}:Q", bin=True),
        y="count()",
    ).transform_filter(brush)
    
    return scatter & (hist_x | hist_y)
