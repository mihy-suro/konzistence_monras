"""
Analýza nekonzistence názvů sloupců v databázi MONRAS.
"""
import sqlite3
from collections import defaultdict
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "monras_import.sqlite"

def analyze_columns():
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = sorted([row[0] for row in cursor.fetchall()])
    print(f"Počet tabulek: {len(tables)}")
    print(f"Tabulky: {', '.join(tables)}")
    print()
    
    # Collect columns from each table
    table_columns = {}
    all_columns = defaultdict(list)  # column -> [tables]
    
    for table in tables:
        cursor.execute(f'PRAGMA table_info("{table}")')
        cols = [row[1] for row in cursor.fetchall()]
        table_columns[table] = cols
        for col in cols:
            all_columns[col].append(table)
    
    # Find columns that are NOT in all tables (potential inconsistencies)
    print("=" * 60)
    print("SLOUPCE KTERÉ NEJSOU VE VŠECH TABULKÁCH")
    print("=" * 60)
    
    # Group by similar column names
    date_variants = {}
    for col in sorted(all_columns.keys()):
        if "datum" in col.lower():
            count = len(all_columns[col])
            date_variants[col] = count
            print(f"{col}: {count}/{len(tables)} tabulek")
    
    print()
    print("=" * 60)
    print("DATUMOVÉ SLOUPCE - PODROBNĚ")
    print("=" * 60)
    
    # Check which date columns each table has
    date_cols_per_table = {}
    for table, cols in table_columns.items():
        date_cols = [c for c in cols if "datum" in c.lower()]
        date_cols_per_table[table] = date_cols
    
    # Group tables by their date column pattern
    patterns = defaultdict(list)
    for table, date_cols in date_cols_per_table.items():
        pattern = tuple(sorted(date_cols))
        patterns[pattern].append(table)
    
    for pattern, tables_list in sorted(patterns.items(), key=lambda x: -len(x[1])):
        print(f"\n{len(tables_list)} tabulek s tímto vzorem:")
        print(f"  Tabulky: {', '.join(tables_list)}")
        print(f"  Datumové sloupce: {list(pattern)}")
    
    # Analyze nuklidy
    print()
    print("=" * 60)
    print("ANALÝZA RADIONUKLIDŮ")
    print("=" * 60)
    
    nuklidy_all = set()
    for table in tables:
        try:
            cursor.execute(f'SELECT DISTINCT nuklid FROM "{table}" WHERE nuklid IS NOT NULL')
            nuklidy = {row[0] for row in cursor.fetchall()}
            nuklidy_all.update(nuklidy)
        except sqlite3.OperationalError:
            print(f"  {table}: sloupec 'nuklid' neexistuje")
    
    print(f"\nCelkem unikátních radionuklidů: {len(nuklidy_all)}")
    print(f"Seznam: {sorted(nuklidy_all)}")
    
    # Count per nuklid
    print("\n--- Počty záznamů podle radionuklidu ---")
    nuklid_counts = {}
    for table in tables:
        try:
            cursor.execute(f'SELECT nuklid, COUNT(*) FROM "{table}" WHERE nuklid IS NOT NULL GROUP BY nuklid')
            for row in cursor.fetchall():
                nuklid = row[0]
                count = row[1]
                nuklid_counts[nuklid] = nuklid_counts.get(nuklid, 0) + count
        except sqlite3.OperationalError:
            pass
    
    for nuklid, count in sorted(nuklid_counts.items(), key=lambda x: -x[1]):
        print(f"  {nuklid}: {count:,}")
    
    conn.close()

if __name__ == "__main__":
    analyze_columns()
