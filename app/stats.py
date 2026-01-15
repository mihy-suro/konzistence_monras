"""
Statistical functions for outlier detection.

Implements tolerance intervals similar to R's tolerance package.
"""
import numpy as np
from scipy import stats
from typing import Optional, Tuple


def tolerance_factor_normal(n: int, alpha: float = 0.05, P: float = 0.95, side: int = 1) -> float:
    """
    Calculate the tolerance factor k for normal distribution.
    
    One-sided upper tolerance limit: mean + k * std
    
    Based on the formula for one-sided normal tolerance intervals.
    Uses the non-central t-distribution approach.
    
    Args:
        n: Sample size
        alpha: Significance level (default 0.05 for 95% confidence)
        P: Coverage proportion (e.g., 0.90, 0.95, 0.99)
        side: 1 for one-sided (upper), 2 for two-sided
    
    Returns:
        Tolerance factor k
    """
    if n < 2:
        return np.nan
    
    if side == 1:
        # One-sided tolerance interval
        # k = t_{1-alpha, n-1, delta} / sqrt(n)
        # where delta = z_P * sqrt(n) is the non-centrality parameter
        z_p = stats.norm.ppf(P)
        
        # Approximation using the Howe method (simpler, widely used)
        # k ≈ z_P + z_{1-alpha} * sqrt((1 + z_P^2/2) / (n-1))
        z_alpha = stats.norm.ppf(1 - alpha)
        k = z_p + z_alpha * np.sqrt((1 + z_p**2 / 2) / (n - 1))
        
        return k
    else:
        # Two-sided - use chi-squared approach
        z_p = stats.norm.ppf((1 + P) / 2)
        chi2_val = stats.chi2.ppf(1 - alpha, n - 1)
        k = z_p * np.sqrt((n - 1) * (1 + 1/n) / chi2_val)
        return k


def lognormal_tolerance_interval(
    data: np.ndarray,
    alpha: float = 0.05,
    P: float = 0.95,
    side: int = 1
) -> Tuple[Optional[float], Optional[float]]:
    """
    Calculate tolerance interval assuming log-normal distribution.
    
    Args:
        data: Array of positive values
        alpha: Significance level (default 0.05)
        P: Coverage proportion (0.90, 0.95, or 0.99)
        side: 1 for one-sided upper, 2 for two-sided
    
    Returns:
        Tuple of (lower_bound, upper_bound). For one-sided upper, lower is None.
    """
    # Filter positive values only
    data = np.array(data)
    data = data[data > 0]
    data = data[~np.isnan(data)]
    
    n = len(data)
    if n < 2:
        return (None, None)
    
    # Transform to log scale
    log_data = np.log(data)
    
    # Calculate mean and std on log scale
    log_mean = np.mean(log_data)
    log_std = np.std(log_data, ddof=1)  # Sample std
    
    # Get tolerance factor
    k = tolerance_factor_normal(n, alpha, P, side)
    
    if side == 1:
        # One-sided upper
        upper_log = log_mean + k * log_std
        upper = np.exp(upper_log)
        return (None, upper)
    else:
        # Two-sided
        lower_log = log_mean - k * log_std
        upper_log = log_mean + k * log_std
        return (np.exp(lower_log), np.exp(upper_log))


def calculate_tolerance_intervals(
    data: np.ndarray,
    alpha: float = 0.05
) -> dict:
    """
    Calculate TI90, TI95, TI99 for the given data.
    
    Args:
        data: Array of values (assumes log-normal distribution)
        alpha: Significance level
    
    Returns:
        Dict with keys 'ti90', 'ti95', 'ti99', 'mean', 'n'
    """
    data = np.array(data)
    data = data[~np.isnan(data)]
    data = data[data > 0]
    
    if len(data) < 2:
        return {
            'ti90': None,
            'ti95': None,
            'ti99': None,
            'mean': None,
            'n': 0
        }
    
    _, ti90 = lognormal_tolerance_interval(data, alpha=alpha, P=0.90, side=1)
    _, ti95 = lognormal_tolerance_interval(data, alpha=alpha, P=0.95, side=1)
    _, ti99 = lognormal_tolerance_interval(data, alpha=alpha, P=0.99, side=1)
    
    return {
        'ti90': ti90,
        'ti95': ti95,
        'ti99': ti99,
        'mean': np.mean(data),
        'n': len(data)
    }
