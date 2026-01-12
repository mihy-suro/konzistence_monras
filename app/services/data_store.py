"""
Správa dat v paměti a serializace pro dcc.Store.

Funkce pro:
- Konverzi DataFrame na JSON pro dcc.Store
- Deserializaci JSON zpět na DataFrame
- Zachování datových typů (datetime, nullable int, ...)
- Komprese velkých datasetů

dcc.Store ukládá data do session storage prohlížeče,
takže musí být serializovatelná do JSON.
"""

import pandas as pd
import json
from typing import Optional


def dataframe_to_store(df: pd.DataFrame) -> dict:
    """
    Konvertuje DataFrame na dict pro uložení do dcc.Store.
    
    Zachovává:
    - Datové typy sloupců
    - Datetime hodnoty (jako ISO string)
    - Nullable typy (Int64, Float64, boolean)
    
    Args:
        df: DataFrame k serializaci
        
    Returns:
        Dict s daty a metadaty pro rekonstrukci
    """
    # TODO: Implementovat serializaci
    return {
        "data": df.to_dict("records"),
        "dtypes": df.dtypes.astype(str).to_dict(),
        "columns": list(df.columns),
    }


def store_to_dataframe(store_data: dict) -> pd.DataFrame:
    """
    Rekonstruuje DataFrame z dat v dcc.Store.
    
    Args:
        store_data: Dict z dcc.Store
        
    Returns:
        Rekonstruovaný DataFrame se správnými typy
    """
    # TODO: Implementovat deserializaci
    if store_data is None:
        return pd.DataFrame()
    
    df = pd.DataFrame(store_data["data"])
    # Obnovení datových typů
    # ...
    return df


def compress_dataframe(df: pd.DataFrame, max_rows: int = 10000) -> pd.DataFrame:
    """
    Komprimuje DataFrame pokud je příliš velký pro session storage.
    
    Args:
        df: DataFrame k kompresi
        max_rows: Maximální počet řádků
        
    Returns:
        Komprimovaný DataFrame
    """
    # TODO: Implementovat kompresi/sampling
    if len(df) > max_rows:
        return df.sample(n=max_rows, random_state=42)
    return df
