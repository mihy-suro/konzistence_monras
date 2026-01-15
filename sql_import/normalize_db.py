"""
Sjednocení názvů sloupců a filtrace radionuklidů v MONRAS databázi.

Řeší:
1. Nekonzistentní názvy datumových sloupců mezi tabulkami
2. Odstranění nepotřebných radionuklidů

Spuštění:
    uv run python normalize_db.py --dry-run    # pouze ukáže co se provede
    uv run python normalize_db.py              # provede změny
"""
import sqlite3
import argparse
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "monras_import.sqlite"

# Radionuklidy k ponechání (ostatní budou smazány)
KEEP_NUKLIDS = {
    "Cs 137",
    "Pb 210", 
    "K 40",
    "Be 7",
    "Sr 90",
    "H 3",
    "SumaB",
    "Pu 239",
    "Pu 238",
    "Pu 239+240",  # alternativní zápis
    "Na 22",
}

# Mapování nekonzistentních názvů sloupců na jednotný název
# klíč = starý název, hodnota = nový název
COLUMN_RENAMES = {
    # Datum odběru - sjednotit na datum_odberu_utc
    "datum_cas_odber_zac_utc": "datum_odberu_utc",
    "datum_cas_odber_zac_utc_2": None,  # smazat duplicitní
    
    # Konec odběru - sjednotit na konec_odberu_utc  
    "datum_cas_odber_kon_utc": "konec_odberu_utc",
    "datum_cas_odber_kon_utc_2": None,  # smazat duplicitní
    
    # Datum měření - sjednotit na datum_mereni_utc
    "datum_cas_mereni_utc": "datum_mereni_utc",
    "datum_a_cas_mereni_utc": "datum_mereni_utc",
    
    # Referenční datum - sjednotit na referencni_datum_utc
    "referencni_datum_a_cas_utc": "referencni_datum_utc",
    "referencni_datum_a_cas_mistni_cas": "referencni_datum_mistni_cas",
    
    # Datum vytvoření/změny - sjednotit
    "datum_a_cas_vytvoreni_mistni_cas": "datum_vytvoreni_mistni_cas",
    "datum_vytvoreni_mistni_cas_a": "datum_vytvoreni_mistni_cas",
    "datum_a_cas_vytvoreni_mistni_cas_1": None,  # duplicitní, smazat
    "datum_vytvoreni_mistni_cas_b": None,  # duplicitní, smazat
    "datum_a_cas_zmeny_mistni_cas": "datum_zmeny_mistni_cas",
    "datum_zmeny_mistni_cas_a": "datum_zmeny_mistni_cas",
    "datum_a_cas_zmeny_mistni_cas_1": None,  # duplicitní, smazat
    "datum_zmeny_mistni_cas_b": None,  # duplicitní, smazat
    
    # Datum zrušení - oprava překlepu
    "datu_zruseni": "datum_zruseni",
}


def get_tables(conn: sqlite3.Connection) -> list[str]:
    """Vrátí seznam všech tabulek."""
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    return [row[0] for row in cursor.fetchall()]


def get_columns(conn: sqlite3.Connection, table: str) -> list[str]:
    """Vrátí seznam sloupců tabulky."""
    cursor = conn.cursor()
    cursor.execute(f'PRAGMA table_info("{table}")')
    return [row[1] for row in cursor.fetchall()]


def rename_columns(conn: sqlite3.Connection, dry_run: bool = True):
    """Přejmenuje nekonzistentní sloupce na jednotný formát."""
    tables = get_tables(conn)
    
    print("=" * 60)
    print("PŘEJMENOVÁNÍ SLOUPCŮ")
    print("=" * 60)
    
    for table in tables:
        columns = get_columns(conn, table)
        renames_for_table = []
        drops_for_table = []
        
        for col in columns:
            if col in COLUMN_RENAMES:
                new_name = COLUMN_RENAMES[col]
                if new_name is None:
                    drops_for_table.append(col)
                elif new_name not in columns:  # nepřejmenovávat pokud cíl už existuje
                    renames_for_table.append((col, new_name))
        
        if renames_for_table or drops_for_table:
            print(f"\n{table}:")
            
            if not dry_run:
                # SQLite nepodporuje přímé přejmenování, musíme tabulku přestavět
                # Ale od SQLite 3.25 podporuje ALTER TABLE RENAME COLUMN
                cursor = conn.cursor()
                
                for old_name, new_name in renames_for_table:
                    print(f"  RENAME: {old_name} -> {new_name}")
                    try:
                        cursor.execute(f'ALTER TABLE "{table}" RENAME COLUMN "{old_name}" TO "{new_name}"')
                    except sqlite3.OperationalError as e:
                        print(f"    CHYBA: {e}")
                
                # Pro odstranění sloupců bychom museli tabulku přestavět
                # To je komplexnější, prozatím jen upozorníme
                for col in drops_for_table:
                    print(f"  DROP: {col} (nutno přestavět tabulku)")
                
                conn.commit()
            else:
                for old_name, new_name in renames_for_table:
                    print(f"  [DRY-RUN] RENAME: {old_name} -> {new_name}")
                for col in drops_for_table:
                    print(f"  [DRY-RUN] DROP: {col}")


def delete_nuklids(conn: sqlite3.Connection, dry_run: bool = True):
    """Smaže záznamy radionuklidů, které nejsou v KEEP_NUKLIDS."""
    tables = get_tables(conn)
    
    print()
    print("=" * 60)
    print("FILTRACE RADIONUKLIDŮ")
    print("=" * 60)
    print(f"Ponechané radionuklidy: {sorted(KEEP_NUKLIDS)}")
    print()
    
    total_deleted = 0
    total_kept = 0
    
    cursor = conn.cursor()
    
    for table in tables:
        columns = get_columns(conn, table)
        
        if "nuklid" not in columns:
            print(f"{table}: sloupec 'nuklid' neexistuje, přeskakuji")
            continue
        
        # Spočítej záznamy před
        cursor.execute(f'SELECT COUNT(*) FROM "{table}"')
        count_before = cursor.fetchone()[0]
        
        # Spočítej záznamy k ponechání
        placeholders = ",".join(["?" for _ in KEEP_NUKLIDS])
        cursor.execute(
            f'SELECT COUNT(*) FROM "{table}" WHERE nuklid IN ({placeholders})',
            list(KEEP_NUKLIDS)
        )
        count_keep = cursor.fetchone()[0]
        
        count_delete = count_before - count_keep
        
        print(f"{table}:")
        print(f"  Celkem: {count_before:,}, Ponechat: {count_keep:,}, Smazat: {count_delete:,}")
        
        if count_delete > 0:
            if not dry_run:
                cursor.execute(
                    f'DELETE FROM "{table}" WHERE nuklid NOT IN ({placeholders})',
                    list(KEEP_NUKLIDS)
                )
                conn.commit()
                print(f"  ✓ Smazáno {count_delete:,} záznamů")
            else:
                print(f"  [DRY-RUN] Bude smazáno {count_delete:,} záznamů")
        
        total_deleted += count_delete
        total_kept += count_keep
    
    print()
    print(f"CELKEM: Ponechat {total_kept:,}, Smazat {total_deleted:,}")


def vacuum_db(conn: sqlite3.Connection, dry_run: bool = True):
    """Provede VACUUM pro zmenšení databáze."""
    if dry_run:
        print("\n[DRY-RUN] VACUUM by zmenšil databázi")
    else:
        print("\nProvádím VACUUM...")
        conn.execute("VACUUM")
        print("✓ VACUUM dokončen")


def main():
    parser = argparse.ArgumentParser(description="Normalizace MONRAS databáze")
    parser.add_argument("--dry-run", action="store_true", help="Pouze ukázat co se provede")
    parser.add_argument("--skip-rename", action="store_true", help="Přeskočit přejmenování sloupců")
    parser.add_argument("--skip-nuklids", action="store_true", help="Přeskočit filtraci radionuklidů")
    args = parser.parse_args()
    
    print(f"Databáze: {DB_PATH}")
    print(f"Režim: {'DRY-RUN (žádné změny)' if args.dry_run else 'OSTRÝ BĚCH!'}")
    print()
    
    conn = sqlite3.connect(str(DB_PATH))
    
    try:
        if not args.skip_rename:
            rename_columns(conn, dry_run=args.dry_run)
        
        if not args.skip_nuklids:
            delete_nuklids(conn, dry_run=args.dry_run)
        
        if not args.dry_run:
            vacuum_db(conn, dry_run=args.dry_run)
        
        print()
        print("=" * 60)
        print("HOTOVO" if not args.dry_run else "DRY-RUN DOKONČEN")
        print("=" * 60)
        
    finally:
        conn.close()


if __name__ == "__main__":
    main()
