
---

## 4) Komponenty

### 4.1 Sidebar (filtry)
- Dataset dropdown: název tabulky v SQLite
- Nuklid dropdown
- OM dropdown
- Jednotka dropdown
- Reset button (reset selection)

> Filtry jsou dynamické: options se načítají z DB (DISTINCT) pro aktuální tabulku.

### 4.2 Scatter plot (Plotly, `dcc.Graph`)
- X osa: datum (např. `datum_cas_mereni_utc` nebo `datum_cas_odber_zac_utc` – dle toho, co má dataset)
- Y osa: hodnota (`hodnota`)
- `customdata`: `row_key` (ne index)
- `dragmode="select"` nebo `"lasso"`
- zvýraznění výběru přes `selectedpoints`

### 4.3 AgGrid
- `rowData`: filtrovaná data
- sloupce (MVP): datum, hodnota, nuklid, jednotka, odber_misto, id_zppr_vzorek
- nastavit `getRowId` na `row_key` (stabilní ID v gridu)
- paginace: client-side v MVP, server-side až později

---

## 5) Data Contract (minimální sada sloupců)

Každý dataset/tabulka musí pro MVP dodat:

| Role | Doporučený sloupec |
|------|---------------------|
| unikátní část ID | `id_zppr_vzorek` |
| radionuklid | `nuklid` |
| datum | `datum_cas_mereni_utc` (nebo jiný, ale konzistentní) |
| hodnota | `hodnota` |
| jednotka | `jednotka` |
| OM | `odber_misto` nebo `id_om` |

Aplikace si z `(id_zppr_vzorek, nuklid)` vytvoří `row_key`.

---

## 6) Crossfilter mechanismus (scatter → tabulka)

### 6.1 Scatter: selectedpoints + customdata
- `customdata = row_key`
- z `selectedData["points"]` vyextrahovat `row_key` list:
  - `selected_keys = [p["customdata"] for p in selectedData["points"]]`

### 6.2 Tabulka: filtrování podle `selected_keys`
- pokud `selected_keys` existuje:
  - `df_table = df[df["row_key"].isin(selected_keys)]`
- jinak:
  - `df_table = df`

### 6.3 Reset
- reset tlačítko “vynuluje” selection stav:
  - callback ignoruje `selectedData` a chová se jako by nebyl výběr
- v praxi:
  - držet `selection_state` (např. `dcc.Store`) nebo jednoduše v callbacku:
    - pokud trigger == reset, nastavit `selected_keys = None`

> Důležité: `selectedpoints` je jen vizuální highlight. Nečekat, že změní `selectedData`.

---

## 7) State Management (MVP)

### MVP varianta: jeden callback
Jediný callback, který řeší:
- načtení dat z DB dle filtrů
- extrakci selection z grafu
- sestavení scatter figury se zvýrazněním
- sestavení grid dat
- info text (Vybráno X z Y)

#### Inputs
- dataset dropdown
- filtry (nuklid, OM, jednotka)
- scatter `selectedData`
- reset `n_clicks`

#### Outputs
- scatter `figure`
- aggrid `rowData` (nebo container s gridem)
- info text
- (volitelně) options pro dropdowny filtrů

---

## 8) DB access (minimální query plán)

### 8.1 `get_tables()`
- seznam tabulek: `SELECT name FROM sqlite_master WHERE type='table' ...`

### 8.2 `get_filter_options(table, col)`
- dropdown hodnoty: `SELECT DISTINCT col FROM table WHERE col IS NOT NULL ORDER BY col`

### 8.3 `get_plot_data(table, filters, max_points)`
- základní dataset pro scatter + tabulku:
  - `SELECT id_zppr_vzorek, nuklid, datum..., hodnota, jednotka, odber_misto, id_om ... FROM table WHERE ...`
- aplikovat WHERE dle filtrů
- limitovat `max_points` (např. 10k) pro MVP

Pozn.: Pro MVP je OK tahat stejný DF pro scatter i tabulku. Později se to rozdělí (downsampling pro scatter, server-side paging pro grid).

---

## 9) AgGrid doporučené nastavení (MVP)

- `getRowId`: `"params.data.row_key"`
- `defaultColDef`:
  - sortable: true
  - filter: true
  - resizable: true
- paginace:
  - jednoduchá, client-side (např. 100–500 řádků / page)

---

## 10) Implementační kroky (MVP)

1) Layout: sidebar + scatter + grid + info
2) Dataset dropdown (tabulky ze SQLite)
3) Načtení dat podle filtrů (bez selection)
4) Scatter s `customdata=row_key` a `dragmode="select"`
5) Extrakce `selected_keys` ze `selectedData`
6) Filtrování tabulky přes `row_key`
7) Reset button (vynulování selection)
8) Dynamické filter options (DISTINCT)

---

## 11) Co odložit (až po MVP)

- bidirekční crossfilter (tabulka → graf)
- histogram
- outlier detection / referenční intervaly
- server-side pagination
- downsampling (LTTB)
- export CSV

---

*Dokument: MRS Viewer Minimal v1.1 – 2026-01-15*
