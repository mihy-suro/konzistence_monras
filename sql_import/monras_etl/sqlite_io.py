import os
import glob
import sqlite3
from pathlib import Path
from typing import List, Optional
import numpy as np

import pandas as pd
from tqdm import tqdm

from .config import Config
from .naming import table_name_from_filename
from .header_detect import detect_sheet_and_header
from .schema import shorten_columns, build_column_type_map, infer_sqlite_types_explicit
from .datetime_parse import (
    detect_datetime_columns,
    is_utc_column,
    parse_datetime_series,
    datetime_to_storage
)
from .import_logger import ImportLogger

# Kotvy pro detekci hlavičky - normalizované názvy (bez jednotek, lowercase, mezery místo _)
# Stačí shoda s několika z nich
EXPECTED_HEADER = [
    "id zppr vzorek",
    "id om",
    "odběrové místo",
    "stálé",
    "zeměpisná délka",
    "zeměpisná šířka",
    "provozovatel",
    "monitorovaná položka",
    "datum a čas odběru začátek",
    "datum a čas odběru konec",
    "datum a čas měření",
    "nuklid",
    "hodnota",
    "jednotka",
    "nejistota",
    "množství",
    "poznámka admin",
]

def apply_pragmas(conn: sqlite3.Connection, pragmas: dict) -> None:
    cur = conn.cursor()
    for k, v in (pragmas or {}).items():
        cur.execute(f"PRAGMA {k}={v}")
    conn.commit()

def table_exists(conn: sqlite3.Connection, table: str) -> bool:
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (table,))
    return cur.fetchone() is not None

def create_table(conn: sqlite3.Connection, table: str, cols: List[str], types: List[str], if_exists: str) -> None:
    cur = conn.cursor()
    if if_exists == "replace":
        cur.execute(f'DROP TABLE IF EXISTS "{table}"')

    col_defs = ", ".join([f'"{c}" {t}' for c, t in zip(cols, types)])
    cur.execute(f'CREATE TABLE IF NOT EXISTS "{table}" ({col_defs})')
    conn.commit()

def create_indexes(conn: sqlite3.Connection, table: str, indexes: List[List[str]]) -> None:
    cur = conn.cursor()
    for cols in indexes or []:
        idx_name = f"idx_{table}_" + "_".join(cols)
        cols_sql = ", ".join([f'"{c}"' for c in cols])
        cur.execute(f'CREATE INDEX IF NOT EXISTS "{idx_name}" ON "{table}" ({cols_sql})')
    conn.commit()

def iter_input_files(cfg: dict, base_dir: Path) -> List[str]:
    roots = cfg["input"]["roots"]
    pattern = cfg["input"].get("glob", "*.xlsx")
    recursive = bool(cfg["input"].get("recursive", False))

    files = []
    for root in roots:
        root = os.path.expandvars(root)
        # Resolvuj relativní cesty vůči umístění config.yaml
        root_path = base_dir / root
        if recursive:
            files.extend(glob.glob(str(root_path / "**" / pattern), recursive=True))
        else:
            files.extend(glob.glob(str(root_path / pattern), recursive=False))

    files = [f for f in files if not os.path.basename(f).startswith("~$")]
    return sorted(set(files))

def load_one_xlsx(conn: sqlite3.Connection, xlsx_path: str, cfg: dict, logger: ImportLogger) -> None:
    # excel detect
    excel_cfg = cfg["excel"]
    sheet, header_row = detect_sheet_and_header(
        xlsx_path=xlsx_path,
        expected_header=EXPECTED_HEADER,
        max_rows=int(excel_cfg["max_header_scan_rows"]),
        min_hits=int(excel_cfg["header_match"]["min_hits"]),
        min_ratio=float(excel_cfg["header_match"]["min_ratio"]),
    )

    # table name
    nam = cfg["naming"]
    table = table_name_from_filename(
        xlsx_path,
        drop_years=bool(nam["drop_years"]),
        drop_trailing_version_suffix=bool(nam["drop_trailing_version_suffix"]),
        keep_max_words=int(nam["keep_max_words"]),
        max_len=int(nam["max_len"]),
    )

    out_cfg = cfg["output"]
    if_exists = out_cfg["if_exists"].lower()
    if if_exists not in {"replace", "append", "fail"}:
        raise ValueError("output.if_exists musí být replace | append | fail")
    if if_exists == "fail" and table_exists(conn, table):
        raise RuntimeError(f"Tabulka '{table}' existuje a if_exists=fail.")

    # read xlsx
    df = pd.read_excel(
        xlsx_path,
        sheet_name=sheet,
        header=header_row - 1,
        engine="openpyxl",
        dtype=object
    ).dropna(how="all")

    file_basename = os.path.basename(xlsx_path)
    
    # rename columns
    sch = cfg["schema"]
    df.columns = shorten_columns(list(df.columns), sch.get("column_aliases", {}), max_len=64)

    # datetime convert
    dt_cfg = sch["datetime"]
    dt_cols = detect_datetime_columns(df.columns, dt_cfg["detect_regex"])

    for c in dt_cols:
        utc = is_utc_column(c, dt_cfg["utc_regex"])
        original_values = df[c].copy()
        df[c] = parse_datetime_series(df[c], assume_utc=utc)
        
        # Loguj neúspěšné parsování datetime
        failed_mask = original_values.notna() & df[c].isna()
        if failed_mask.any():
            for idx in df.index[failed_mask][:10]:  # Max 10 příkladů
                logger.add_datetime_error(
                    file_basename, sheet, c, 
                    int(idx) + header_row + 1,  # Excel řádek (1-based)
                    original_values.loc[idx]
                )

        # uložit do SQLite jako ISO / unix ms
        df[c] = datetime_to_storage(
            df[c],
            assume_utc=utc,
            store_as=dt_cfg["store_as"],
            iso_format_naive=dt_cfg["iso_format_naive"],
            iso_format_utc=dt_cfg["iso_format_utc"],
        )

    # types - explicitní konfigurace
    column_type_map = build_column_type_map(sch.get("column_types"))
    fallback_type = sch.get("fallback_type", "TEXT")
    col_types = infer_sqlite_types_explicit(list(df.columns), column_type_map, fallback_type)

    # Validace a oprava hodnot před zápisem
    SQLITE_INT_MAX = 2**63 - 1
    SQLITE_INT_MIN = -(2**63)
    
    for col, col_type in zip(df.columns, col_types):
        if col_type == "INTEGER":
            # Kontrola přetečení INTEGER
            numeric = pd.to_numeric(df[col], errors="coerce")
            overflow_mask = (numeric > SQLITE_INT_MAX) | (numeric < SQLITE_INT_MIN)
            if overflow_mask.any():
                for idx in df.index[overflow_mask][:10]:
                    logger.add_value_overflow(
                        file_basename, sheet, col,
                        int(idx) + header_row + 1,
                        df.loc[idx, col]
                    )
                # Nahraď přetečené hodnoty NULL
                df.loc[overflow_mask, col] = None
        
        elif col_type == "REAL":
            # Kontrola příliš velkých REAL hodnot
            numeric = pd.to_numeric(df[col], errors="coerce")
            # IEEE 754 double max ~1.8e308, ale SQLite může mít problémy s extrémními hodnotami
            overflow_mask = (numeric.abs() > 1e100) & numeric.notna()
            if overflow_mask.any():
                for idx in df.index[overflow_mask][:10]:
                    logger.add(
                        file_basename, sheet, col,
                        int(idx) + header_row + 1,
                        str(df.loc[idx, col]),
                        "EXTREME_VALUE",
                        f"Extrémně velká hodnota (>1e100)"
                    )
                # Tyto hodnoty ponecháme, jen je zalogujeme

    # create table
    create_table(conn, table, list(df.columns), col_types, if_exists=if_exists)

    # insert - bez method="multi" kvůli limitu SQLite proměnných (max 999)
    chunk_rows = int(cfg["sqlite"]["chunk_rows"])
    # Dynamicky omezit chunk podle počtu sloupců
    max_vars = 999
    cols_count = len(df.columns)
    safe_chunk = max(1, max_vars // cols_count)
    actual_chunk = min(chunk_rows, safe_chunk)
    
    for start in range(0, len(df), actual_chunk):
        df.iloc[start:start + actual_chunk].to_sql(
            table, conn, if_exists="append", index=False
        )

    # indexes (jen existující sloupce)
    if bool(cfg["sqlite"].get("create_indexes", True)):
        idx_cfg = cfg["sqlite"].get("indexes", [])
        existing = set(df.columns)
        filtered = []
        for cols in idx_cfg:
            cols2 = [c for c in cols if c in existing]
            if cols2:
                filtered.append(cols2)
        if filtered:
            create_indexes(conn, table, filtered)

    tqdm.write(f"OK: {file_basename} -> {table} (sheet='{sheet}', rows={len(df)})")

def run_import(config: Config) -> None:
    cfg = config.raw
    base_dir = config.base_dir
    
    # Inicializace loggeru problémů
    logger = ImportLogger()
    
    # Resolvuj cestu k SQLite databázi relativně k config.yaml
    db_path = os.path.expandvars(cfg["output"]["sqlite_path"])
    db_path = str(base_dir / db_path)
    os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)

    files = iter_input_files(cfg, base_dir)
    if not files:
        print("Nenalezeny žádné XLSX soubory.")
        return

    conn = sqlite3.connect(db_path)
    try:
        apply_pragmas(conn, cfg["sqlite"].get("pragmas", {}))

        for f in tqdm(files, desc="Import XLSX", unit="soubor"):
            try:
                load_one_xlsx(conn, f, cfg, logger)
            except Exception as e:
                logger.add_general_error(os.path.basename(f), "", str(e))
                tqdm.write(f"CHYBA: {f}: {e}")
    finally:
        conn.close()
    
    # Zápis reportu problémů
    if logger.has_problems():
        report_path = base_dir / "import_problems.txt"
        logger.write_report(report_path)
        logger.print_summary()
        print(f"📄 Report problémů uložen: {report_path}")
