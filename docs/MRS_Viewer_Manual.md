# MRS Viewer - Uživatelský a technický manuál

## Obsah

1. [Přehled aplikace](#přehled-aplikace)
2. [Architektura systému](#architektura-systému)
3. [Backend - SQLite databáze](#backend---sqlite-databáze)
4. [Frontend komponenty](#frontend-komponenty)
5. [Konfigurace aplikace](#konfigurace-aplikace)
6. [Workflow pro identifikaci problematických hodnot](#workflow-pro-identifikaci-problematických-hodnot)
7. [Klávesové zkratky](#klávesové-zkratky)
8. [Řešení problémů](#řešení-problémů)

---

## Přehled aplikace

**MRS Viewer** je interaktivní webová aplikace pro vizualizaci a analýzu dat z Monitorovací sítě radiační situace (MONRAS). Aplikace umožňuje:

- Prohlížení časových řad měření radioaktivity
- Statistickou analýzu pomocí tolerančních intervalů (TI)
- Identifikaci odlehlých hodnot (outlierů)
- Filtrování dat podle nuklidu, lokality a dodavatele
- Export vybraných dat

### Hlavní případy užití

| Případ užití | Popis |
|-------------|-------|
| Kontrola konzistence | Identifikace hodnot mimo toleranční intervaly |
| Analýza trendů | Sledování vývoje aktivity v čase |
| Porovnání lokalit | Srovnání hodnot mezi odběrovými místy |
| Validace dat | Kontrola dat před publikací |

---

## Architektura systému

```
┌─────────────────────────────────────────────────────────────────┐
│                        MRS Viewer                                │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │
│  │   Layout     │  │  Callbacks   │  │      Pages           │   │
│  │  (routing)   │◄─┤  (logika)    │◄─┤  home/docs/config    │   │
│  └──────────────┘  └──────────────┘  └──────────────────────┘   │
│         │                 │                     │                │
│         ▼                 ▼                     ▼                │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                    Data Layer                            │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐  │    │
│  │  │   Cache     │  │     DB      │  │    Config       │  │    │
│  │  │ (rychlé     │◄─┤  (SQLite)   │  │   (YAML)        │  │    │
│  │  │  filtry)    │  │             │  │                 │  │    │
│  │  └─────────────┘  └─────────────┘  └─────────────────┘  │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │  monras_import  │
                    │    .sqlite      │
                    └─────────────────┘
```

### Struktura projektu

```
konzistence_monras/
├── run.py                 # Vstupní bod aplikace
├── config.yaml            # Konfigurace aplikace
├── monras_import.sqlite   # Databáze s daty
│
├── app/
│   ├── app.py            # Inicializace Dash aplikace
│   ├── layout.py         # Hlavní layout + routing
│   ├── ids.py            # Konstanty ID komponent
│   ├── config.py         # Loader konfigurace
│   │
│   ├── pages/            # Stránky aplikace
│   │   ├── home.py       # Hlavní dashboard
│   │   ├── docs.py       # Dokumentace
│   │   └── config_editor.py  # Editor konfigurace
│   │
│   ├── callbacks/        # Reaktivní logika
│   │   ├── routing.py    # Navigace mezi stránkami
│   │   ├── filters.py    # Aktualizace filtrů
│   │   ├── selection.py  # Výběr bodů v grafu
│   │   ├── main_content.py   # Hlavní graf a tabulka
│   │   ├── side_charts.py    # Boxplot a histogram
│   │   └── reference.py      # Referenční období
│   │
│   ├── data/             # Datová vrstva
│   │   ├── db.py         # Přístup k SQLite
│   │   └── cache.py      # Cache filtrů
│   │
│   └── utils/            # Pomocné funkce
│       └── excel_reader.py
│
├── sql_import/           # ETL skripty pro import dat
│   ├── xlsx_to_sqlite.py
│   └── monras_etl/
│
└── docs/                 # Dokumentace
```

---

## Backend - SQLite databáze

### Struktura databáze

Databáze `monras_import.sqlite` obsahuje tabulky podle typu vzorků (matric). Každá tabulka má standardizovanou strukturu:

```sql
CREATE TABLE nazev_matrice (
    -- Identifikátory
    id_zppr_vzorek TEXT,      -- Unikátní ID vzorku
    id_zppr_analyzat TEXT,    -- ID analýzy
    
    -- Časové údaje
    datum TEXT,               -- Datum odběru (YYYY-MM-DD)
    datum_mereni_utc TEXT,    -- Datum měření v UTC
    
    -- Měřená data
    hodnota REAL,             -- Naměřená hodnota aktivity
    nejistota REAL,           -- Nejistota měření
    jednotka TEXT,            -- Jednotka (Bq/kg, Bq/l, ...)
    
    -- Metadata
    nuklid TEXT,              -- Měřený nuklid (Cs-137, K-40, ...)
    odber_misto TEXT,         -- Lokalita odběru
    dodavatel_dat TEXT,       -- Organizace provádějící měření
    pod_mva INTEGER,          -- 1 = hodnota pod mezí detekce (MVA)
    
    -- Pomocné
    row_key TEXT PRIMARY KEY  -- Unikátní klíč řádku
);
```

### Dostupné tabulky (matrice)

| Tabulka | Popis | Typické nuklidy |
|---------|-------|-----------------|
| `pitna_voda` | Pitná voda | H-3, Ra-226, Ra-228 |
| `povrchova_voda` | Povrchové vody | Cs-137, Sr-90 |
| `mleko_surove` | Syrové mléko | Cs-137, K-40, Sr-90 |
| `maso` | Maso | Cs-137, K-40 |
| `zelenina` | Zelenina | Cs-137, K-40 |
| `ovoce` | Ovoce | Cs-137, K-40 |
| `obiloviny` | Obiloviny | Cs-137, K-40, Sr-90 |
| `houby` | Houby | Cs-137, K-40 |
| `ryby` | Ryby | Cs-137, K-40 |
| `puda` | Půda | Cs-137, K-40 |
| `spady` | Atmosférické spady | Cs-137, Be-7 |
| ... | ... | ... |

### Indexy pro rychlé filtrování

Databáze automaticky vytváří indexy na často filtrovaných sloupcích:

```sql
CREATE INDEX idx_pitna_voda_nuklid ON pitna_voda(nuklid);
CREATE INDEX idx_pitna_voda_odber_misto ON pitna_voda(odber_misto);
CREATE INDEX idx_pitna_voda_datum_mereni_utc ON pitna_voda(datum_mereni_utc);
```

### Práce s databází přímo

```python
import sqlite3

# Připojení k databázi
conn = sqlite3.connect('monras_import.sqlite')
cursor = conn.cursor()

# Příklad: Statistika Cs-137 v mléce
cursor.execute("""
    SELECT 
        COUNT(*) as pocet,
        AVG(hodnota) as prumer,
        MIN(hodnota) as minimum,
        MAX(hodnota) as maximum
    FROM mleko_surove 
    WHERE nuklid = 'Cs-137' 
      AND pod_mva != 1
""")
print(cursor.fetchone())

conn.close()
```

---

## Frontend komponenty

### 1. Navigační lišta (Navbar)

**Umístění:** Horní část aplikace (vždy viditelná)

| Prvek | Funkce |
|-------|--------|
| MRS Viewer | Odkaz na hlavní stránku (home) |
| Návod | Zobrazí dokumentaci |
| Nastavení | Editor konfigurace |
| GitHub | Odkaz na repozitář |

### 2. Sidebar - Filtry

**Umístění:** Levý panel na hlavní stránce

#### Dataset (tabulka)
- **Typ:** Dropdown (single-select)
- **Funkce:** Výběr datové matrice (pitná voda, mléko, ...)
- **Provázání:** Změna datasetu aktualizuje všechny ostatní filtry a grafy

#### Nuklid
- **Typ:** Dropdown (single-select)
- **Funkce:** Filtrování podle konkrétního nuklidu
- **Provázání:** 
  - Možnosti se aktualizují podle vybraného datasetu
  - Ovlivňuje scatter plot, boxplot, histogram i tabulku

#### Odběrové místo
- **Typ:** Dropdown (multi-select)
- **Funkce:** Filtrování podle lokality/lokalit
- **Provázání:** Možnosti závisí na datasetu a konfiguraci prefiltrů

#### Dodavatel dat
- **Typ:** Dropdown (multi-select)
- **Funkce:** Filtrování podle organizace provádějící měření
- **Provázání:** Možnosti závisí na datasetu

#### Rozsah dat v grafu
- **Typ:** RangeSlider
- **Funkce:** Výběr časového rozsahu pro zobrazení
- **Provázání:** 
  - Ovlivňuje scatter plot (zobrazené body)
  - Neovlivňuje výpočet statistik

#### Referenční období (pro TI)
- **Typ:** RangeSlider
- **Funkce:** Definice období pro výpočet tolerančních intervalů
- **Provázání:**
  - Ovlivňuje výpočet TI čar ve scatter plotu
  - Zelené pozadí označuje referenční období
  - Body mimo TI se zvýrazní jako outliery

#### Počet binů histogramu
- **Typ:** Slider
- **Funkce:** Nastavení rozlišení histogramu
- **Rozsah:** 5-100 (výchozí 25)

#### MVA toggle
- **Typ:** Button (toggle)
- **Funkce:** Zobrazit/skrýt hodnoty pod mezí detekce
- **Indikace:** Zelený = zobrazeno, šedý = skryto

#### Reset výběru
- **Typ:** Button
- **Funkce:** Zrušení výběru bodů v grafu

### 3. Scatter Plot (Časová řada)

**Umístění:** Hlavní oblast, levá část

```
    hodnota
      ▲
      │     ●           TI99 ─────────────────
      │   ● ●  ●        TI95 ─────────────────
      │  ●●●●●●●●       TI90 ─────────────────
      │ ●●●●●●●●●●●
      │●●●●●●●●●●●●●    Medián ═══════════════
      │ ●●●●●●●●●●●
      │  ●●●●●●●●
      │   ● ●  ●        
      │     ○           ← outlier (mimo TI)
      └───────────────────────────────────────► datum
          │←  ref. období  →│
```

#### Prvky grafu:

| Prvek | Barva | Popis |
|-------|-------|-------|
| Normální body | Modrá | Měření v rámci TI |
| Vybrané body | Červená | Interaktivně vybrané |
| Outliery | Fialová | Mimo zvolený toleranční interval |
| MVA body | Šedá/průhledná | Hodnoty pod mezí detekce |
| Referenční období | Zelené pozadí | Oblast pro výpočet TI |
| TI90 linie | Modrá čárkovaná | 90% toleranční interval |
| TI95 linie | Oranžová čárkovaná | 95% toleranční interval |
| TI99 linie | Červená čárkovaná | 99% toleranční interval |
| Medián | Černá plná | Střední hodnota ref. období |

#### Interakce:

| Akce | Efekt |
|------|-------|
| Klik na bod | Výběr jednoho bodu |
| Lasso select | Výběr více bodů |
| Box select | Výběr obdélníkem |
| Scroll | Zoom |
| Dvojklik | Reset zoomu |
| Shift + Klik | Přidat/odebrat z výběru |

### 4. Boxplot

**Umístění:** Hlavní oblast, pravá horní část

Zobrazuje rozložení hodnot podle odběrového místa nebo jiné kategorie.

```
         ┌───┬───┐
         │   │   │    whisker (max)
         ├───┼───┤
         │   █   │    75. percentil
         │   █   │    medián
         │   █   │    25. percentil
         ├───┼───┤
         │   │   │    whisker (min)
         └───┴───┘
        lokalita A
```

- Vybrané body se zvýrazní červeně
- Při více než 10 kategoriích se zobrazí souhrnný boxplot

### 5. Histogram

**Umístění:** Hlavní oblast, pravá dolní část

```
    počet
      ▲
      │    ████
      │   ██████  ░░
      │  ████████░░░░
      │ ██████████░░░░░
      └────────────────────► hodnota
      
      ████ = všechna data
      ░░░░ = vybraná data
```

- Šedá/modrá: distribuce všech dat
- Červená: distribuce vybraných bodů
- Počet binů nastavitelný sliderem

### 6. Datová tabulka (AG Grid)

**Umístění:** Spodní část hlavní oblasti

| Sloupec | Popis |
|---------|-------|
| Datum | Datum odběru/měření |
| Hodnota | Naměřená aktivita |
| Nejistota | Nejistota měření |
| MVA | Příznak pod mezí detekce |
| Nuklid | Měřený nuklid |
| Jednotka | Jednotka měření |
| Odběrové místo | Lokalita |
| Dodavatel | Měřící organizace |
| ID Vzorek | Unikátní identifikátor |

#### Funkce tabulky:
- **Řazení:** Klik na hlavičku sloupce
- **Filtrování:** Ikona filtru v hlavičce
- **Stránkování:** Navigace pod tabulkou
- **Výběr řádků:** Synchronizován s grafem
- **Změna šířky:** Tažení okrajů sloupců

---

## Konfigurace aplikace

### Soubor config.yaml

```yaml
# =============================================================================
# MRS Viewer Configuration
# =============================================================================

server:
  port: 8050
  host: "127.0.0.1"
  debug: true

database:
  path: "../monras_import.sqlite"   # Relativní cesta k DB
  max_points: 50000                  # Max bodů v grafu

# Layout dimensions
layout:
  sidebar_width: 2
  main_area_width: 10
  scatter_height: 420
  boxplot_height: 420
  histogram_height: 420
  table_height: 420

# Scatter plot appearance
scatter:
  marker_size_normal: 8
  marker_size_selected: 10
  marker_size_outlier: 12
  opacity_normal: 0.7
  opacity_selected: 0.9
  opacity_dimmed: 0.3
  default_color: "steelblue"
  selection_color: "red"
  outlier_color: "purple"
  reference_fill_color: "rgba(144, 238, 144, 0.2)"
  ti90_color: "blue"
  ti95_color: "orange"
  ti99_color: "red"

# Histogram settings
histogram:
  default_bins: 25
  min_bins: 5
  max_bins: 100
  bin_step: 5

# Data table
table:
  page_size: 50
  min_column_width: 100

# Hidden tables (won't appear in dropdown)
hidden_tables:
  - "_import_log"
  - "sqlite_sequence"

# =============================================================================
# Table Prefilters
# =============================================================================
# Define which data to load for specific tables

table_prefilters:
  pitna_voda:
    nuklidy:
      - "H-3"
      - "Ra-226"
      - "Ra-228"
    exclude_mva: false
    
  mleko_surove:
    nuklidy:
      - "Cs-137"
      - "K-40"
    lokality: []           # Prázdné = všechny
    dodavatele: []
    exclude_mva: false
    min_date: "2000-01-01"
    max_date: null         # null = bez omezení
```

### Úprava konfigurace z aplikace

1. Klikněte na **Nastavení** v navigaci
2. Upravte YAML v textovém editoru
3. Klikněte **Uložit**
4. Klikněte **Reload** pro aplikování změn
5. Přejděte na hlavní stránku

### Prefiltery - omezení načítaných dat

Prefiltery umožňují načíst jen relevantní data pro specifickou analýzu:

```yaml
table_prefilters:
  nazev_tabulky:
    nuklidy:          # Seznam povolených nuklidů
      - "Cs-137"
    lokality:         # Seznam povolených lokalit
      - "Praha"
      - "Brno"
    dodavatele:       # Seznam povolených dodavatelů
      - "SURO"
    exclude_mva: true # Vyloučit hodnoty pod MVA
    min_date: "2010-01-01"
    max_date: "2023-12-31"
```

---

## Workflow pro identifikaci problematických hodnot

### Workflow 1: Základní kontrola outlierů

**Cíl:** Najít hodnoty výrazně odlišné od běžného rozsahu

1. **Vyberte dataset** (např. `mleko_surove`)
2. **Vyberte nuklid** (např. `Cs-137`)
3. **Nastavte referenční období** na historická data (např. 10-90%)
4. **Pozorujte scatter plot:**
   - Fialové body = outliery mimo TI99
   - Zkontrolujte jejich kontext (lokalita, datum, dodavatel)
5. **Použijte lasso select** pro výběr podezřelých bodů
6. **Zkontrolujte v tabulce** detaily vybraných měření

```
Příklad interpretace:
─────────────────────
• Jeden izolovaný outlier → možná chyba měření
• Skupina outlierů ze stejné lokality → lokální kontaminace?
• Outliery od jednoho dodavatele → systematická chyba?
• Postupný trend → změna podmínek
```

### Workflow 2: Porovnání lokalit

**Cíl:** Identifikovat lokality s neobvyklými hodnotami

1. **Vyberte dataset a nuklid**
2. **Ponechte všechny lokality** (nevybírat v dropdown)
3. **Sledujte boxplot:**
   - Porovnejte mediány mezi lokalitami
   - Hledejte lokality s velkým rozptylem
   - Identifikujte lokality s outliery
4. **Klikněte na podezřelou lokalitu** v boxplotu
5. **Filtrujte na tuto lokalitu** v dropdown
6. **Analyzujte časový průběh** ve scatter plotu

### Workflow 3: Kontrola časové konzistence

**Cíl:** Najít náhlé změny nebo skoky v datech

1. **Vyberte dataset, nuklid a lokalitu**
2. **Nastavte široké referenční období** (0-100%)
3. **Použijte zoom** pro přiblížení časového úseku
4. **Hledejte:**
   - Náhlé skoky v hodnotách
   - Změny variability
   - Sezónní vzorce
5. **Pro podezřelé úseky:**
   - Zúžte referenční období na "normální" data
   - Outliery se automaticky zvýrazní

### Workflow 4: Validace nových dat

**Cíl:** Ověřit konzistenci nově importovaných dat

1. **V konfiguraci nastavte `min_date`** na datum importu
2. **Restart aplikace** nebo reload konfigurace
3. **Procházejte jednotlivé datasety a nuklidy**
4. **Pro každou kombinaci:**
   - Nastavte ref. období na historická data (např. `max_date` den před importem)
   - Nová data by měla být v podobném rozsahu
   - Zaznamenejte outliery pro další kontrolu

### Workflow 5: Detekce systematických chyb

**Cíl:** Najít problémy specifické pro dodavatele

1. **Vyberte dataset a nuklid**
2. **Postupně vybírejte jednotlivé dodavatele**
3. **Pro každého porovnejte:**
   - Střední hodnotu (medián v boxplotu)
   - Variabilitu (šířka boxu)
   - Počet outlierů
4. **Pokud jeden dodavatel vybočuje:**
   - Zkontrolujte časový průběh
   - Ověřte, zda jde o všechny nuklidy
   - Zaznamenejte pro další šetření

### Příklad analýzy: Podezřelá hodnota Cs-137 v mléce

```
Situace: V grafu je jeden bod výrazně nad ostatními

Kroky:
1. Kliknu na bod → zvýrazní se v tabulce
2. Zjistím: hodnota 15 Bq/l, lokalita "Farma XY", datum 2024-03-15
3. Průměr ostatních hodnot: 0.5 Bq/l → 30x vyšší!

Kontroly:
□ Je správná jednotka? (Bq/l vs Bq/kg)
□ Není to MVA hodnota špatně importovaná?
□ Jsou v okolí podobně vysoké hodnoty?
□ Má stejný dodavatel podobné problémy jinde?

Závěr:
- Pokud izolovaná hodnota bez vysvětlení → pravděpodobně chyba
- Pokud skupinka hodnot → možný reálný nález, vyžaduje šetření
```

---

## Klávesové zkratky

| Zkratka | Funkce |
|---------|--------|
| `Shift + Klik` | Přidat/odebrat bod z výběru |
| `Scroll` | Zoom v grafu |
| `Dvojklik` | Reset zoomu |
| `Esc` | Zrušit výběr (v některých prohlížečích) |

---

## Řešení problémů

### Aplikace se nespustí

```
Chyba: ModuleNotFoundError
Řešení: pip install -r requirements.txt
```

```
Chyba: Database not found
Řešení: Zkontrolujte cestu v config.yaml → database.path
```

### Grafy se nezobrazují

- Zkontrolujte, zda je vybrán dataset
- Zkontrolujte, zda dataset obsahuje data pro vybraný nuklid
- Zkontrolujte prefiltery v konfiguraci

### Pomalé načítání

- Snižte `max_points` v konfiguraci
- Použijte prefiltery pro omezení dat
- Zkontrolujte, zda existují indexy v databázi

### Chybí některé tabulky

- Zkontrolujte `hidden_tables` v konfiguraci
- Ověřte, zda tabulka existuje v databázi:
  ```sql
  SELECT name FROM sqlite_master WHERE type='table';
  ```

### Outliery se nezobrazují

- Ověřte, že referenční období obsahuje dostatek dat (min. 10 bodů)
- Zkontrolujte, že ref. období nezahrnuje všechna data

---

## Technické poznámky

### Výpočet tolerančních intervalů

Toleranční intervaly jsou počítány na základě dat v referenčním období:

```python
# Předpoklad log-normálního rozdělení
log_values = np.log(values[values > 0])
mean = np.mean(log_values)
std = np.std(log_values, ddof=1)

# k-faktory pro jednostranný TI (95% coverage, 95% confidence)
# závisí na počtu vzorků
k = tolerance_factor(n=len(values), coverage=0.95, confidence=0.95)

# Horní mez
upper_limit = np.exp(mean + k * std)
```

### Callback dependencies

```
DROPDOWN_DATASET
      │
      ├──► DROPDOWN_NUKLID (options)
      ├──► DROPDOWN_OM (options)
      ├──► DROPDOWN_DODAVATEL (options)
      │
      └──► [všechny filtry] ──► SCATTER_PLOT
                              ├──► BOXPLOT
                              ├──► HISTOGRAM
                              └──► AGGRID_TABLE

SCATTER_PLOT (selectedData)
      │
      ├──► BOXPLOT (zvýraznění)
      ├──► HISTOGRAM (překryv)
      └──► AGGRID_TABLE (výběr řádků)
```

### Cachování

Při startu aplikace se načítají:
- Seznam tabulek
- Distinktní hodnoty filtrů pro každou tabulku
- Indexy se vytvoří automaticky

Cache se invaliduje při:
- Reloadu konfigurace (tlačítko Reload)
- Restartu aplikace

---

*Verze dokumentace: 1.0*  
*Poslední aktualizace: 2026-01-16*
