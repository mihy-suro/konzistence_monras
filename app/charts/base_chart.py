"""
Základní konfigurace a témata pro Altair grafy.

Definuje:
- Společné téma pro všechny grafy (barvy, fonty)
- Základní konfiguraci os a legend
- Helper funkce pro formátování

Všechny ostatní chart moduly by měly používat tuto konfiguraci
pro konzistentní vzhled.
"""

import altair as alt

# Definice barevné palety pro MonRaS
MONRAS_COLORS = {
    "primary": "#0d6efd",
    "secondary": "#6c757d",
    "success": "#198754",
    "danger": "#dc3545",
    "warning": "#ffc107",
    "info": "#0dcaf0",
}

# Barevná škála pro kategorie
CATEGORY_COLORS = [
    "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd",
    "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf",
]


def configure_altair():
    """Nastaví globální konfiguraci Altair."""
    # TODO: Implementovat globální téma
    pass


def get_base_chart(width: int = 400, height: int = 300) -> alt.Chart:
    """
    Vrátí základní Chart s výchozí konfigurací.
    
    Args:
        width: Šířka grafu v pixelech
        height: Výška grafu v pixelech
        
    Returns:
        alt.Chart s konfigurací
    """
    # TODO: Implementovat base chart
    return alt.Chart().properties(width=width, height=height)
