import sqlite3
from pathlib import Path

db_path = Path(__file__).parent.parent / "monras_import.sqlite"
conn = sqlite3.connect(db_path)
cur = conn.cursor()

cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cur.fetchall()
print("Tabulky:", [t[0] for t in tables])

if tables:
    cur.execute(f'PRAGMA table_info("{tables[0][0]}")')
    cols = cur.fetchall()
    print("\nSloupce:")
    for c in cols:
        print(f"  {c[1]}: {c[2]}")

conn.close()
