"""Skript pro nalezení extrémních hodnot v Excel souborech."""
import pandas as pd
from pathlib import Path
import numpy as np

data_dir = Path(__file__).parent.parent / "data"

SQLITE_INT_MAX = 9223372036854775807

print(f"Prohledávám: {data_dir}")
print("=" * 80)

for xlsx in sorted(data_dir.rglob("*.xlsx")):
    try:
        # Načti všechny listy
        xl = pd.ExcelFile(xlsx)
        for sheet_name in xl.sheet_names:
            df = pd.read_excel(xl, sheet_name=sheet_name)
            for col in df.columns:
                if pd.api.types.is_numeric_dtype(df[col]):
                    max_val = df[col].max()
                    min_val = df[col].min()
                    
                    if pd.notna(max_val):
                        # Kontrola přetečení SQLite INTEGER
                        if abs(max_val) > SQLITE_INT_MAX or abs(min_val) > SQLITE_INT_MAX:
                            print(f"❌ PŘETEČENÍ: {xlsx.name} [{sheet_name}]")
                            print(f"   Sloupec: {col}")
                            print(f"   Max: {max_val}, Min: {min_val}")
                            # Ukaž problematické řádky
                            problematic = df[(df[col].abs() > SQLITE_INT_MAX)]
                            if not problematic.empty:
                                print(f"   Problematické hodnoty:")
                                print(problematic[[col]].to_string())
                            print()
                        elif abs(max_val) > 10**15 or abs(min_val) > 10**15:
                            print(f"⚠️  VELKÁ HODNOTA: {xlsx.name} [{sheet_name}]")
                            print(f"   Sloupec: {col}, Max: {max_val}, Min: {min_val}")
                            print()
    except Exception as e:
        print(f"❌ CHYBA při čtení {xlsx.name}: {e}")
        print()

print("=" * 80)
print("Hotovo.")
