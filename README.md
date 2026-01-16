# ☢️ MRS Viewer

**Interaktivní aplikace pro vizualizaci a analýzu dat z Monitorovací sítě radiační situace (MONRAS)**

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Dash](https://img.shields.io/badge/Dash-2.x-green.svg)
![License](https://img.shields.io/badge/License-Internal-red.svg)

---

## 🎯 O aplikaci

MRS Viewer je webová aplikace postavená na frameworku [Dash](https://dash.plotly.com/) určená pro:

- 📊 **Vizualizaci časových řad** měření radioaktivity
- 📈 **Statistickou analýzu** pomocí tolerančních intervalů (TI)
- 🔍 **Identifikaci outlierů** a podezřelých hodnot
- 🗂️ **Sběr problematických záznamů** do zásobníku s exportem do Excelu
- 📋 **Porovnání dat** mezi lokalitami a dodavateli

### Screenshot

![MRS Viewer Screenshot](assets/screenshot.png)

---

## 🚀 Rychlý start

### Požadavky

- Python 3.10+
- SQLite databáze `monras_import.sqlite`

### Instalace

```bash
# Klonování repozitáře
git clone https://github.com/your-org/konzistence_monras.git
cd konzistence_monras

# Instalace závislostí (doporučeno přes uv)
uv sync

# Nebo klasicky přes pip
pip install -e .
```

### Spuštění

```bash
# Přes uv
uv run python run.py

# Nebo přímo
python run.py
```

Aplikace běží na **http://127.0.0.1:8050**

---

## 📖 Dokumentace

Podrobný uživatelský a technický manuál je dostupný:

- **V aplikaci:** klikněte na **Návod** v navigační liště
- **Soubor:** [`app/pages/docs.py`](app/pages/docs.py) (DOCS_CONTENT)

### Obsah dokumentace

1. 📋 Přehled aplikace
2. 🏗️ Architektura systému
3. 🗄️ Backend - SQLite databáze
4. 🖥️ Frontend komponenty
5. ⚙️ Konfigurace aplikace
6. 🔍 Workflow pro analýzu dat
7. ⌨️ Klávesové zkratky
8. 🛠️ Řešení problémů

---

## ✨ Hlavní funkce

### Interaktivní scatter plot
- Výběr bodů pomocí lasso/box select
- Zoom a pan
- Zvýraznění outlierů (mimo TI99)
- Barevné rozlišení podle lokality/dodavatele

### Toleranční intervaly
- Automatický výpočet TI90, TI95, TI99
- Nastavitelné referenční období
- Předpoklad log-normálního rozdělení

### Zásobník podezřelých záznamů
- Sběr problematických hodnot z různých datasetů
- Export do formátovaného Excelu
- Persistentní během navigace v aplikaci

### Log aktivit
- Přehled provedených akcí
- Barevně odlišené typy zpráv
- Časová razítka

---

## 🗂️ Struktura projektu

```
konzistence_monras/
├── run.py                 # Vstupní bod
├── config.yaml            # Konfigurace
├── monras_import.sqlite   # Databáze (není v repo)
│
├── app/
│   ├── app.py            # Inicializace Dash
│   ├── layout.py         # Hlavní layout + routing
│   ├── ids.py            # ID konstant komponent
│   ├── config.py         # Loader konfigurace
│   ├── stats.py          # Statistické výpočty (TI)
│   │
│   ├── pages/            # Stránky
│   │   ├── home.py       # Hlavní dashboard
│   │   ├── docs.py       # Dokumentace
│   │   └── config_editor.py
│   │
│   ├── callbacks/        # Reaktivní logika
│   │   ├── filters.py
│   │   ├── main_content.py
│   │   ├── suspicious.py
│   │   ├── status_log.py
│   │   └── ...
│   │
│   └── data/             # Datová vrstva
│       ├── db.py
│       └── cache.py
│
├── sql_import/           # ETL skripty pro import dat
│   ├── xlsx_to_sqlite.py
│   └── monras_etl/
│
└── r_scripts/            # Staré R skripty (archiv)
                          # Původní skripty pro generování
                          # statických reportů - pro ilustraci
```

---

## ⚙️ Konfigurace

Hlavní konfigurace je v souboru `config.yaml`:

```yaml
server:
  port: 8050
  debug: true

database:
  path: "../monras_import.sqlite"
  max_points: 50000

# Prefiltery pro omezení načítaných dat
table_prefilters:
  pitna_voda:
    nuklidy: ["H-3", "Ra-226"]
    exclude_mva: false
```

Konfiguraci lze upravit přímo v aplikaci: **Nastavení** → editace → **Uložit** → **Reload**

---

## 🔧 Vývoj

### Technologie

- **Backend:** Python, SQLite
- **Frontend:** Dash, Plotly, AG Grid, Bootstrap 5
- **Styling:** dash-bootstrap-components

### Přidání nové funkcionality

1. Přidejte ID konstanty do `app/ids.py`
2. Vytvořte callback v `app/callbacks/`
3. Zaregistrujte v `app/callbacks/__init__.py`
4. Aktualizujte layout v `app/pages/home.py`
5. Aktualizujte dokumentaci v `app/pages/docs.py`

---

## 📝 Licence

Interní použití SÚRO.

---

## 👥 Kontakt

Pro dotazy a hlášení chyb kontaktujte správce aplikace.
