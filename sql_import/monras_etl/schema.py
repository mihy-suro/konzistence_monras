from typing import Dict, List, Tuple, Optional
import re

from .header_detect import norm_text
from .naming import slugify_identifier

def make_unique(names: List[str]) -> List[str]:
    seen = {}
    out = []
    for n in names:
        k = seen.get(n, 0)
        if k == 0:
            out.append(n)
        else:
            out.append(f"{n}_{k+1}")
        seen[n] = k + 1
    return out

def shorten_columns(excel_cols: List[str], column_aliases: Dict[str, str], max_len: int = 64) -> List[str]:
    # alias mapu normalizujeme na norm_text klíče
    aliases_norm = {norm_text(k): v for k, v in (column_aliases or {}).items()}

    out = []
    for c in excel_cols:
        key = norm_text(c)
        if key in aliases_norm:
            out.append(aliases_norm[key])
        else:
            out.append(slugify_identifier(c, max_len=max_len))
    return make_unique(out)

def build_column_type_map(column_types: Optional[Dict[str, List[str]]]) -> Dict[str, str]:
    """
    Vytvoří mapu sloupec -> typ z konfigurace column_types.
    
    column_types má strukturu:
      integer: [col1, col2, ...]
      real: [col3, col4, ...]
      text: [col5, col6, ...]
      datetime: [col7, col8, ...]  # mapuje se na INTEGER (unix_ms)
    """
    # Mapování konfiguračních názvů na SQLite typy
    type_aliases = {
        "INTEGER": "INTEGER",
        "REAL": "REAL", 
        "TEXT": "TEXT",
        "DATETIME": "INTEGER",  # datetime jako unix_ms
        "BOOLEAN": "INTEGER",   # boolean jako 0/1
    }
    
    type_map = {}
    if not column_types:
        return type_map
    
    for type_name, columns in column_types.items():
        sqlite_type = type_aliases.get(type_name.upper(), type_name.upper())
        for col in (columns or []):
            type_map[col.lower()] = sqlite_type
    
    return type_map

def infer_sqlite_types_explicit(cols: List[str], column_type_map: Dict[str, str], fallback_type: str = "TEXT") -> List[str]:
    """
    Určí SQLite typy pro sloupce na základě explicitní mapy.
    Sloupce neuvedené v mapě dostanou fallback_type.
    """
    out = []
    for c in cols:
        t = column_type_map.get(c.lower(), fallback_type.upper())
        out.append(t)
    return out

# Zachováno pro zpětnou kompatibilitu
def compile_type_rules(type_rules: List[dict]) -> List[Tuple[re.Pattern, str]]:
    compiled = []
    for rule in type_rules:
        compiled.append((re.compile(rule["regex"], re.IGNORECASE), rule["type"].upper()))
    return compiled

def infer_sqlite_types(cols: List[str], compiled_rules: List[Tuple[re.Pattern, str]]) -> List[str]:
    out = []
    for c in cols:
        t = "TEXT"
        for pat, typ in compiled_rules:
            if pat.search(c):
                t = typ
                break
        out.append(t)
    return out
