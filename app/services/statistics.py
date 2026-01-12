"""
Výpočty statistik pro MonRaS data.

Funkce pro:
- Základní statistiky (mean, median, std, min, max)
- Statistiky podle skupin (kraj, nuklid, ...)
- Percentily a kvantily
- Počty chybějících hodnot

Všechny funkce jsou čisté - bez vedlejších efektů.
"""

import pandas as pd
import numpy as np
from typing import Optional


def calculate_statistics(df: pd.DataFrame, column: str) -> dict:
    """
    Vypočítá základní statistiky pro numerický sloupec.
    
    Args:
        df: DataFrame s daty
        column: Název numerického sloupce
        
    Returns:
        Dict se statistikami
    """
    # TODO: Implementovat výpočet statistik
    if column not in df.columns:
        return {}
    
    series = pd.to_numeric(df[column], errors="coerce")
    
    return {
        "count": int(series.count()),
        "missing": int(series.isna().sum()),
        "mean": float(series.mean()) if not series.isna().all() else None,
        "median": float(series.median()) if not series.isna().all() else None,
        "std": float(series.std()) if not series.isna().all() else None,
        "min": float(series.min()) if not series.isna().all() else None,
        "max": float(series.max()) if not series.isna().all() else None,
        "q25": float(series.quantile(0.25)) if not series.isna().all() else None,
        "q75": float(series.quantile(0.75)) if not series.isna().all() else None,
    }


def calculate_column_stats(df: pd.DataFrame) -> pd.DataFrame:
    """
    Vypočítá statistiky pro všechny numerické sloupce.
    
    Args:
        df: DataFrame s daty
        
    Returns:
        DataFrame se statistikami jako řádky
    """
    # TODO: Implementovat statistiky pro všechny sloupce
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    stats = []
    
    for col in numeric_cols:
        col_stats = calculate_statistics(df, col)
        col_stats["column"] = col
        stats.append(col_stats)
    
    return pd.DataFrame(stats)


def calculate_grouped_statistics(
    df: pd.DataFrame,
    value_column: str,
    group_column: str,
) -> pd.DataFrame:
    """
    Vypočítá statistiky seskupené podle kategorického sloupce.
    
    Args:
        df: DataFrame s daty
        value_column: Numerický sloupec pro statistiky
        group_column: Kategorický sloupec pro seskupení
        
    Returns:
        DataFrame se statistikami pro každou skupinu
    """
    # TODO: Implementovat grouped statistics
    return df.groupby(group_column)[value_column].agg([
        "count", "mean", "median", "std", "min", "max"
    ]).reset_index()
