# SQL Import - XLSX do SQLite

Nástroj pro import XLSX souborů z MonRaS do SQLite databáze.

## Rychlý start

```powershell
# Aktivace virtuálního prostředí
.\.venv\Scripts\Activate.ps1

# Spuštění importu
python sql_import/xlsx_to_sqlite.py
```

Import automaticky načte konfiguraci z `config.yaml` ve stejném adresáři.

## Struktura adresáře

```
sql_import/
├── xlsx_to_sqlite.py      # Hlavní vstupní skript
├── config.yaml            # Konfigurace importu
├── import_problems.txt    # Report problémů (generuje se při importu)
├── README.md              # Tato dokumentace
└── monras_etl/            # Importní moduly
    ├── config.py          # Načítání YAML konfigurace
    ├── datetime_parse.py  # Parsování a oprava datetime hodnot
    ├── header_detect.py   # Detekce hlavičky v XLSX
    ├── import_logger.py   # Logování problémů během importu
    ├── naming.py          # Generování názvů tabulek
    ├── schema.py          # Mapování sloupců a typů
    └── sqlite_io.py       # Hlavní importní logika
```

## Konfigurace (config.yaml)

### Vstupní soubory

```yaml
input:
  roots:                    # Adresáře s XLSX soubory (relativní k config.yaml)
    - "../data/Polozky_PR"
    - "../data/Polozky_ZP"
  glob: "*.xlsx"            # Pattern pro vyhledávání souborů
  recursive: false          # Rekurzivní prohledávání
```

### Výstupní databáze

```yaml
output:
  sqlite_path: "../monras_import.sqlite"  # Cesta k SQLite DB
  if_exists: "replace"      # replace | append | fail
```

### Detekce hlavičky

```yaml
excel:
  max_header_scan_rows: 80  # Max řádků pro hledání hlavičky
  header_match:
    min_hits: 5             # Min počet rozpoznaných sloupců
    min_ratio: 0.10         # Min poměr rozpoznaných sloupců
```

### Pojmenování tabulek

```yaml
naming:
  drop_years: true          # Odstranit roky z názvu (Maso 2024 -> maso)
  drop_trailing_version_suffix: true  # Odstranit _2, _v2 atd.
  keep_max_words: 4         # Max počet slov v názvu
  max_len: 48               # Max délka názvu
```

### SQLite nastavení

```yaml
sqlite:
  pragmas:
    journal_mode: "WAL"     # Write-Ahead Logging pro lepší výkon
    synchronous: "NORMAL"
    temp_store: "MEMORY"
  chunk_rows: 5000          # Velikost chunků pro INSERT
  create_indexes: true      # Vytvořit indexy
  indexes:                  # Definice indexů
    - ["id_zppr_vzorek"]
    - ["id_om"]
    - ["datum_cas_odber_zac_utc"]
```

## Schema databáze

### Datové typy

| Konfigurační typ | SQLite typ | Popis |
|-----------------|------------|-------|
| `integer` | INTEGER | Celá čísla |
| `real` | REAL | Desetinná čísla |
| `text` | TEXT | Textové řetězce |
| `datetime` | INTEGER | Unix timestamp v milisekundách |
| `boolean` | INTEGER | 0 nebo 1 |

### Aliasy sloupců

Dlouhé názvy sloupců z XLSX jsou mapovány na kratší:

| Originální název | Alias v DB |
|-----------------|------------|
| `ID ZPPR vzorek` | `id_zppr_vzorek` |
| `ID_OM` | `id_om` |
| `Zeměpisná délka [°]` | `lon_deg` |
| `Zeměpisná šířka [°]` | `lat_deg` |
| `Datum a čas odběru začátek [UTC]` | `datum_cas_odber_zac_utc` |
| `Množství` | `mnozstvi` |
| `Nuklid` | `nuklid` |
| `Hodnota` | `hodnota` |
| `Nejistota` | `nejistota` |

### Typické sloupce

```sql
-- INTEGER sloupce
id_zppr_vzorek, id_om

-- REAL sloupce  
lon_deg, lat_deg, alt_m, mnozstvi, hodnota, hodnota_cista, nejistota

-- TEXT sloupce
odber_misto, jednotka_mnozstvi, nuklid, jednotka, poznamka_admin

-- DATETIME sloupce (INTEGER jako unix_ms)
datum_cas_odber_zac_utc, datum_cas_odber_kon_utc, datum_cas_mereni_utc
```

### Práce s datetime

Datetime hodnoty jsou uloženy jako **INTEGER** (Unix timestamp v milisekundách od 1970-01-01).

```sql
-- Filtrování podle data (rok 2023)
SELECT * FROM maso 
WHERE datum_cas_odber_zac_utc BETWEEN 1672531200000 AND 1704067199000;

-- Převod na čitelný formát
SELECT datetime(datum_cas_odber_zac_utc / 1000, 'unixepoch') as datum
FROM maso;
```

## Zpracování problémů

### Report problémů

Během importu se generuje soubor `import_problems.txt` s nalezenými problémy:

- **DATETIME_ERROR** - Neplatný formát data/času
- **VALUE_OVERFLOW** - Hodnota příliš velká pro SQLite INTEGER
- **EXTREME_VALUE** - Extrémně velká REAL hodnota (>1e100)
- **GENERAL_ERROR** - Obecná chyba při zpracování

### Automatické opravy

Import automaticky opravuje:

1. **Chybné roky** - Rok < 100 se opraví přičtením 2000 (0013 → 2013)
2. **Prázdné hodnoty** - Různé formy prázdných hodnot (NA, N/A, -, –) se převádí na NULL
3. **Excel serial dates** - Číselné datumy z Excelu se správně parsují

## Struktura výstupní databáze

### Tabulky

Každý XLSX soubor vytváří jednu tabulku. Název tabulky se odvozuje z názvu souboru:

| XLSX soubor | Tabulka |
|-------------|---------|
| `Maso 2024.xlsx` | `maso` |
| `Borůvky brusinky 2024.xlsx` | `boruvky_brusinky` |
| `Pitná voda 2023.xlsx` | `pitna_voda` |

### Indexy

Automaticky se vytvářejí indexy podle konfigurace:

```sql
CREATE INDEX idx_maso_id_zppr_vzorek ON maso(id_zppr_vzorek);
CREATE INDEX idx_maso_id_om ON maso(id_om);
CREATE INDEX idx_maso_datum_cas_odber_zac_utc ON maso(datum_cas_odber_zac_utc);
```

## Rozšíření a údržba

### Přidání nového sloupce

1. Přidej alias do `config.yaml` → `schema.column_aliases`
2. Přidej typ do `schema.column_types` (integer/real/text/datetime)
3. Pokud je potřeba index, přidej do `sqlite.indexes`

### Přidání nového zdroje dat

1. Přidej cestu do `input.roots`
2. Ověř, že struktura XLSX odpovídá očekávané hlavičce

### Změna formátu datetime

V `config.yaml` změň `schema.datetime.store_as`:
- `unix_ms` - INTEGER (milisekundy) - **rychlejší pro filtrování**
- `iso_text` - TEXT (`2024-03-15T14:30:00Z`) - **čitelnější**

## Závislosti

```
pandas>=2.0.0
openpyxl>=3.1.0
pyyaml>=6.0.3
tqdm>=4.67.1
```

## Poznámky

- Soubory začínající `~$` (dočasné Excel soubory) jsou automaticky ignorovány
- Import používá WAL mód pro lepší výkon při zápisu
- Chunk size se automaticky přizpůsobuje počtu sloupců kvůli limitu SQLite proměnných (max 999)
