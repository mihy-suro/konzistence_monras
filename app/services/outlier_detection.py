"""
Detekce outlierů v MonRaS datech.

Implementované metody:
- IQR (Interquartile Range) - robustní vůči extrémním hodnotám
- Z-score - předpokládá normální rozdělení
- Modified Z-score - robustní varianta s MAD

Všechny metody vrací masku outlierů (boolean Series).
"""

import pandas as pd
import numpy as np
from typing import Tuple


def detect_outliers_iqr(
    df: pd.DataFrame,
    column: str,
    threshold: float = 1.5,
) -> Tuple[pd.Series, dict]:
    """
    Detekuje outliery metodou IQR.
    
    Outlier je hodnota mimo interval [Q1 - k*IQR, Q3 + k*IQR],
    kde k je threshold (standardně 1.5).
    
    Args:
        df: DataFrame s daty
        column: Název numerického sloupce
        threshold: Násobitel IQR (1.5 = mild, 3.0 = extreme)
        
    Returns:
        Tuple (boolean maska outlierů, dict s hranicemi)
    """
    # TODO: Implementovat IQR detekci
    series = pd.to_numeric(df[column], errors="coerce")
    
    Q1 = series.quantile(0.25)
    Q3 = series.quantile(0.75)
    IQR = Q3 - Q1
    
    lower_bound = Q1 - threshold * IQR
    upper_bound = Q3 + threshold * IQR
    
    outlier_mask = (series < lower_bound) | (series > upper_bound)
    
    bounds = {
        "Q1": float(Q1),
        "Q3": float(Q3),
        "IQR": float(IQR),
        "lower_bound": float(lower_bound),
        "upper_bound": float(upper_bound),
        "outlier_count": int(outlier_mask.sum()),
    }
    
    return outlier_mask, bounds


def detect_outliers_zscore(
    df: pd.DataFrame,
    column: str,
    threshold: float = 3.0,
) -> Tuple[pd.Series, dict]:
    """
    Detekuje outliery metodou Z-score.
    
    Outlier je hodnota s |z-score| > threshold.
    Předpokládá přibližně normální rozdělení dat.
    
    Args:
        df: DataFrame s daty
        column: Název numerického sloupce
        threshold: Hranice z-score (standardně 3.0)
        
    Returns:
        Tuple (boolean maska outlierů, dict se statistikami)
    """
    # TODO: Implementovat Z-score detekci
    series = pd.to_numeric(df[column], errors="coerce")
    
    mean = series.mean()
    std = series.std()
    
    if std == 0 or pd.isna(std):
        return pd.Series([False] * len(df)), {"error": "Zero standard deviation"}
    
    z_scores = (series - mean) / std
    outlier_mask = z_scores.abs() > threshold
    
    stats = {
        "mean": float(mean),
        "std": float(std),
        "threshold": threshold,
        "outlier_count": int(outlier_mask.sum()),
    }
    
    return outlier_mask, stats


def detect_outliers_modified_zscore(
    df: pd.DataFrame,
    column: str,
    threshold: float = 3.5,
) -> Tuple[pd.Series, dict]:
    """
    Detekuje outliery metodou Modified Z-score (MAD).
    
    Používá medián a MAD (Median Absolute Deviation) místo
    průměru a směrodatné odchylky. Robustnější vůči outlierům.
    
    Args:
        df: DataFrame s daty
        column: Název numerického sloupce
        threshold: Hranice modified z-score (standardně 3.5)
        
    Returns:
        Tuple (boolean maska outlierů, dict se statistikami)
    """
    # TODO: Implementovat Modified Z-score detekci
    series = pd.to_numeric(df[column], errors="coerce")
    
    median = series.median()
    mad = (series - median).abs().median()
    
    if mad == 0:
        return pd.Series([False] * len(df)), {"error": "Zero MAD"}
    
    # Modified z-score: 0.6745 je konstantní faktor pro normální rozdělení
    modified_z = 0.6745 * (series - median) / mad
    outlier_mask = modified_z.abs() > threshold
    
    stats = {
        "median": float(median),
        "mad": float(mad),
        "threshold": threshold,
        "outlier_count": int(outlier_mask.sum()),
    }
    
    return outlier_mask, stats
