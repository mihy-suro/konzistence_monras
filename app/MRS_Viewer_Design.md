# MRS Viewer – Design & Implementation Guide

## 1. Cíl aplikace

MRS Viewer je interaktivní Dash aplikace určená pro:
- vizualizaci dat radiačního monitoringu z centrální SQLite databáze,
- kontrolu konzistence dat,
- detekci podezřelých a odlehlých hodnot pomocí referenčních (predikčních / tolerančních) intervalů,
- interaktivní průzkum dat pomocí crossfilteringu (časová řada ↔ histogram ↔ tabulky).

Aplikace je určena primárně pro **správce databáze / odborného uživatele**, nikoli pro veřejnou prezentaci.

---

## 2. Základní UI layout

### 2.1 Top navbar
- název aplikace: **MRS Viewer**
- navigace:
  - Dashboard
  - Metodika
  - O aplikaci
- stavové informace (volitelné):
  - vybraný dataset
  - počet záznamů v aktuálním pohledu
  - indikace aktivních filtrů

---

### 2.2 Levý sidebar (ovládací panel)

#### A) Dataset selection
- dropdown: výběr tabulky (datasetu) ze SQLite
- dataset metadata (volitelně): časový rozsah, počet záznamů

#### B) Filtry (facets)
- komodita / skupina
- laboratoř
- radionuklid
- odběrové místo (OM) / síť
- jednotka
- platnost / použitelnost / úroveň
- **MVA handling**:
  - checkbox: „Zahrnout hodnoty pod MVA"
  - vizuální odlišení hodnot pod MVA (jiný marker / barva)

Filtry se aplikují **globálně** na celý dashboard.

#### C) Časový rozsah pohledu
- date range picker: definuje, jaká data jsou zobrazena v grafech a tabulkách

#### D) Referenční interval (outlier detection)
- definice referenčního období:
  - `olddata` – začátek referenčních dat
  - `newdata` – konec referenčních dat (hranice vůči „aktuálním" datům)
- volba úrovní:
  - TI90 / TI95 / TI99
- režim:
  - lognormální
  - jednostranný (upper bound)
- volitelně:
  - „počítat referenci pouze z aktuálně filtrovaných dat"

#### E) Ovládání
- **Reset selection** – zruší pouze výběry z grafů (crossfilter)
- **Reset all** – vrátí filtry i referenční interval na default

---

### 2.3 Střední analytická oblast

#### Řada 1 – Grafy

##### Scatterplot (časová řada)
- x: datum (měření / odběru – dle configu)
- y: hodnota
- tolerance / predikční intervaly (overlay)
- outliery vizuálně zvýrazněny
- hodnoty pod MVA odlišeny symbolem / barvou
- interakce:
  - výběr časového intervalu (box / zoom)
  - lasso selection (volitelně)

##### Histogram
- distribuce hodnot z aktuálního pohledu
- respektuje filtry + selection ze scatteru
- interakce:
  - výběr hodnotového rozsahu (tail selection)

**Bidirekční crossfiltering**:
- scatter → histogram → tabulky
- histogram → scatter → tabulky
- výsledný výběr = průnik všech selection stavů

---

#### Řada 2 – Tabulky

##### Detailní tabulka (AgGrid)
- řádky odpovídají aktuálnímu výběru
- defaultní sloupce definované v configu
- možnost přidat další sloupce (multiselect)
- možnost exportu (CSV)

##### Count / aggregation tabulka (AgGrid)
- agregace nad aktuálním výběrem
- volba dimenze:
  - laboratoř
  - radionuklid
  - OM
  - rok
  - jednotka
- metriky:
  - počet záznamů
  - počet outlierů
  - počet hodnot pod MVA

---

## 3. Architektura aplikace

### 3.1 Technologie

- **Dash**
- **Plotly** (doporučeno místo Altairu)
  - důvod: nativní Dash callbacks, stabilní selection API
- **SQLite** jako backend
- **AgGrid** pro tabulky
- pandas / numpy pro výpočty
- (volitelně) Flask-Caching

---

### 3.2 Adresářová struktura

```
app/
├── __init__.py
├── app.py                    # Dash instance, server
├── layout.py                 # Kompozice layoutu
├── ids.py                    # Centralizované ID komponent
│
├── assets/
│   └── styles.css            # CSS styly
│
├── config/
│   ├── app_config.yaml       # Hlavní konfigurace aplikace
│   └── datasets.yaml         # Mapování sloupců pro datasety
│
├── data/
│   ├── __init__.py
│   ├── db.py                 # SQLite connection factory
│   ├── queries.py            # SQL dotazy (DISTINCT, agregace, base view)
│   └── cache.py              # Volitelně: Flask-Caching
│
├── logic/
│   ├── __init__.py
│   ├── selection.py          # Průnik selection stavů, reset token
│   ├── outliers.py           # Tolerance intervaly, flagging outlierů
│   └── transforms.py         # Datové transformace, MVA handling
│
├── components/
│   ├── __init__.py
│   ├── navbar.py             # Top navbar
│   ├── sidebar.py            # Levý panel s filtry
│   ├── plots.py              # Plotly figury (scatter, histogram)
│   └── tables.py             # AgGrid konfigurace
│
└── callbacks/
    ├── __init__.py
    ├── filters.py            # Filtry → store_filters
    ├── crossfilter.py        # Graph selections → store_selection
    ├── visuals.py            # Renderování grafů
    ├── tables.py             # Detail + count tabulky
    └── reset.py              # Reset selection / reset all
```

---

## 4. Stav aplikace (State management)

### 4.1 Canonical state (klíčový princip)

Aplikace musí mít **jediný zdroj pravdy** uložený v `dcc.Store` objektech:

#### `store-filters` (filters_state)
- dataset (vybraná tabulka)
- všechny filtry (nuklid, OM, jednotka, lab, MVA)
- časový rozsah pohledu
- referenční interval (olddata, newdata)
- outlier parametry (TI level, lognorm)

#### `store-selection` (selection_state)
- časový výběr ze scatter plotu (x_range)
- hodnotový výběr z histogramu (value_range)
- seznam vybraných ID (volitelně pro přesnost)
- reset_token (integer pro reset mechanismus)

Všechny vizualizace a tabulky se renderují **výhradně** z těchto stavů.

---

### 4.2 Crossfiltering

- Scatter a histogram **nekomunikují přímo mezi sebou**
- Oba zapisují selection do `selection_state`
- Průnik selection:
  - čas ∩ hodnota ∩ filtry
- Reset:
  - inkrementace `reset_token`

Tím se zabrání cyklickým callbackům.

---

## 5. Outlier detection (podle R skriptů)

### 5.1 Logika

1. Aplikuj globální filtry
2. Odděl referenční data: `olddata < datum ≤ newdata`
3. Na referenčních datech:
   - log-transform hodnot (pro lognormální režim)
   - odhad parametrů (mean, std na log-scale)
4. Spočítej tolerance interval:
   - lognormální distribuce
   - jednostranný (upper bound)
   - P = 0.90 / 0.95 / 0.99
5. Aplikuj limit na aktuální pohled
6. Flaguj outliery (hodnota > TI_upper)

### 5.2 Vizualizace
- horizontální čáry v scatter plotu (TI90 / TI95 / TI99)
- outliery barevně zvýrazněny (červená)
- hodnoty pod MVA jiný symbol (prázdný kroužek)

---

## 6. MVA handling

- `Pod_MVA` = boolean flag v datech
- **UI:**
  - checkbox „Zahrnout hodnoty pod MVA"
- **Vizualizace:**
  - jiný marker (např. otevřený kruh / circle-open)
  - případně jiná barva (šedá)
- **Výchozí chování:**
  - MVA hodnoty **zahrnuty**, ale vizuálně odlišeny
- **Možnost:**
  - nezahrnovat MVA do výpočtu referenčních intervalů (checkbox)

---

## 7. Velká data a výkon

### 7.1 Limity
- **Scatter:**
  - hard limit (např. 50 000 bodů)
  - při překročení: downsampling (např. LTTB algoritmus)
  - zobrazit upozornění uživateli
- **Tabulky:**
  - server-side pagination v AgGrid
  - SQL `LIMIT / OFFSET`

### 7.2 SQL-first přístup
- filtry, agregace, counts → SQLite (WHERE, GROUP BY)
- pandas pouze pro:
  - výpočty TI (statistika)
  - přípravu dat pro grafy

---

## 8. Konfigurace (YAML)

### app_config.yaml
- mapování rolí sloupců:
  - `date_col`: datum měření/odběru
  - `value_col`: naměřená hodnota
  - `unit_col`: jednotka
  - `rn_col`: radionuklid
  - `lab_col`: laboratoř
  - `om_col`: odběrové místo
  - `mva_col`: Pod_MVA flag
- defaultní sloupce pro detail tabulku
- outlier parametry (default TI level, lognorm mode)
- limity pro sampling (max_scatter_points)

### datasets.yaml
- specifické mapování pro jednotlivé tabulky (pokud se liší názvy sloupců)
- umožňuje jednotné UI napříč komoditami

---

## 9. Doporučený postup implementace (iterace)

| Iterace | Název | Popis |
|---------|-------|-------|
| 1 | Skeleton + Dataset Discovery | Layout, připojení SQLite, výběr tabulky |
| 2 | Filtry + Base Query | Dynamické dropdowny, date picker, SQL builder |
| 3 | Scatter + Histogram | Základní grafy bez crossfilter, MVA vizuálně odlišené |
| 4 | AgGrid tabulky | Detail + count tabulka, multiselect sloupců |
| 5 | Crossfilter jednosměrný | dcc.Store, scatter → histogram → tabulky |
| 6 | Bidirekční crossfilter | Histogram → scatter, průnik selection |
| 7 | Outlier detection | Referenční období, TI výpočet, vizualizace |
| 8 | Polish + Optimalizace | Export, error states, downsampling, YAML config |

**Poznámka:** Tabulky (iterace 4) jsou před crossfilterem, aby byl kompletní layout k testování.

---

## 10. Shrnutí hlavních principů

- Plotly místo Altairu
- Jediný canonical state
- Crossfilter přes průnik selection
- Outlier logika oddělena od UI
- MVA jako první-class citizen
- SQL kdekoliv je to možné
- Konfigurace přes YAML, ne v kódu

---

**Tento dokument slouží jako technický blueprint pro implementaci MRS Viewer.**

---

*Dokument aktualizován: 2026-01-15*
