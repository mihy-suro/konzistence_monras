"""
Excel reader module for MonRaS data files.

Automaticky najde správný list v xlsx souboru podle očekávaných hlaviček
a načte data do pandas DataFrame se správnými datovými typy.
"""

import warnings
import pandas as pd
from pathlib import Path
from typing import Optional

# Očekávané hlavičky pro identifikaci správného listu
EXPECTED_HEADERS = [
    "ID_ZPPR_vzorek",
    "ID_OM",
    "Odběrové_místo",
    "Stálé",
    "Zeměpisná_délka",
    "Zeměpisná_šířka",
]

# Sloupce s datumy - budou parsovány jako datetime
DATE_COLUMNS = [
    "Datum_zřízení",
    "Datu_ zrušení",
    "Datum_Odberu_UTC",
    "Datum_odberu_mistni_cas",
    "Konec_odberu_UTC",
    "Konec_odberu_mistni_cas",
    "Referenční_datum_UTC",
    "Referenční_datum_místní_čas",
    "Datum_a_čas_měření_utc",
    "Datum_a_čas_příjmu_utc",
    "Datum_a_čas_příjmu_mistni_cas",
    "Datum_vytvoření_mistni_cas_a",
    "Datum_změny_mistni_cas_a",
    "Datum_vytvoření_mistni_cas_b",
    "Datum_změny_mistni_cas_b",
]

# Sloupce s boolean hodnotami
BOOLEAN_COLUMNS = [
    "Stálé",
    "SparseNetwork",
    "Směsný_vzorek_místně",
    "Směsný_vzorek_časově",
    "Směsný_vzorek_dle_MP",
    "Odběr_producent_a",
    "Odběr_prostý",
    "Odběr_producent_b",
    "Odběr_samosběr",
    "Odběr_nákup",
    "Platnost_a",
    "Platný_záznam_měření",
    "Pod_MVA",
    "Dodána_hodnota_MVA",
    "Exportovat_REM",
    "Platnost_b",
    "Pamatovat",
]

# Sloupce s celými čísly (ID sloupce)
INTEGER_COLUMNS = [
    "ID_ZPPR_vzorek",
    "ID_OM",
    "ID_Provozovatel",
    "ID_Monit_položka_OM",
    "ID_Stát",
    "ID_Kraj",
    "ID_Okres",
    "ID_Obec",
    "ID_Monitorovani",
    "ID_MP",
    "ID_Dodavatele_dat",
    "ID_Síť",
    "ID_Povodí",
    "ID_Změnil",
    "ID_ZPPR",
    "ID_Metoda_měření",
]


def find_data_sheet(excel_file: pd.ExcelFile) -> Optional[str]:
    """
    Najde správný list v Excel souboru podle očekávaných hlaviček.
    
    Args:
        excel_file: Otevřený pd.ExcelFile objekt
        
    Returns:
        Název listu s daty nebo None pokud nebyl nalezen
    """
    for sheet_name in excel_file.sheet_names:
        # Načteme pouze první řádek pro kontrolu hlaviček
        df_header = pd.read_excel(excel_file, sheet_name=sheet_name, nrows=0)
        columns = list(df_header.columns)
        
        # Kontrola, zda list obsahuje očekávané hlavičky
        matches = sum(1 for h in EXPECTED_HEADERS if h in columns)
        if matches >= len(EXPECTED_HEADERS) // 2:  # Alespoň polovina hlaviček
            return sheet_name
    
    return None


def read_monras_excel(
    file_path: str | Path,
    sheet_name: Optional[str] = None,
    parse_dates: bool = True,
    convert_types: bool = True,
) -> pd.DataFrame:
    """
    Načte MonRaS xlsx soubor do pandas DataFrame.
    
    Automaticky najde správný list podle očekávaných hlaviček a správně
    konvertuje datové typy sloupců.
    
    Args:
        file_path: Cesta k xlsx souboru
        sheet_name: Název listu (pokud None, automaticky se vyhledá)
        parse_dates: Zda parsovat datumové sloupce jako datetime
        convert_types: Zda konvertovat datové typy sloupců
        
    Returns:
        pandas DataFrame s načtenými daty
        
    Raises:
        FileNotFoundError: Pokud soubor neexistuje
        ValueError: Pokud nebyl nalezen list s očekávanými hlavičkami
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"Soubor neexistuje: {file_path}")
    
    if not file_path.suffix.lower() == ".xlsx":
        raise ValueError(f"Očekáván xlsx soubor, dostal: {file_path.suffix}")
    
    # Otevření Excel souboru
    excel_file = pd.ExcelFile(file_path)
    
    # Automatické vyhledání správného listu
    if sheet_name is None:
        sheet_name = find_data_sheet(excel_file)
        if sheet_name is None:
            available_sheets = ", ".join(excel_file.sheet_names)
            raise ValueError(
                f"Nebyl nalezen list s očekávanými hlavičkami. "
                f"Dostupné listy: {available_sheets}"
            )
    
    # Načtení dat (datumy konvertujeme manuálně kvůli českému formátu)
    df = pd.read_excel(
        excel_file,
        sheet_name=sheet_name,
    )
    
    # Parsování datumových sloupců s českým formátem (dd.mm.yyyy)
    if parse_dates:
        df = _parse_date_columns(df)
    
    # Konverze datových typů
    if convert_types:
        df = _convert_column_types(df)
    
    # Přidání metadat jako atributy DataFrame
    df.attrs["source_file"] = str(file_path)
    df.attrs["sheet_name"] = sheet_name
    
    return df


def _parse_date_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Parsuje datumové sloupce s českým formátem (dd.mm.yyyy HH:MM).
    
    Args:
        df: DataFrame s datumovými sloupci
        
    Returns:
        DataFrame s parsovanými datumy
    """
    df = df.copy()
    
    # České formáty datumů (od nejspecifičtějšího)
    date_formats = [
        "%d.%m.%Y %H:%M:%S",
        "%d.%m.%Y %H:%M",
        "%d.%m.%Y",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
    ]
    
    for col in DATE_COLUMNS:
        if col in df.columns:
            # Pokud je již datetime, přeskočíme
            if pd.api.types.is_datetime64_any_dtype(df[col]):
                continue
            
            # Zkusíme různé formáty
            parsed = False
            for fmt in date_formats:
                try:
                    df[col] = pd.to_datetime(df[col], format=fmt, errors="raise")
                    parsed = True
                    break
                except (ValueError, TypeError):
                    continue
            
            # Fallback - automatická detekce
            if not parsed:
                try:
                    with warnings.catch_warnings():
                        warnings.filterwarnings("ignore", message="Could not infer format")
                        df[col] = pd.to_datetime(df[col], dayfirst=True, errors="coerce")
                except Exception:
                    pass
    
    return df


def _convert_column_types(df: pd.DataFrame) -> pd.DataFrame:
    """
    Konvertuje sloupce na správné datové typy.
    
    Args:
        df: DataFrame k konverzi
        
    Returns:
        DataFrame s konvertovanými typy
    """
    df = df.copy()
    
    # Konverze boolean sloupců
    for col in BOOLEAN_COLUMNS:
        if col in df.columns:
            # Převod na boolean s podporou NaN hodnot
            df[col] = df[col].map({
                True: True, False: False,
                1: True, 0: False,
                "True": True, "False": False,
                "Ano": True, "Ne": False,
                "ano": True, "ne": False,
                "1": True, "0": False,
            }).astype("boolean")  # Nullable boolean
    
    # Konverze integer sloupců (s podporou NaN - použijeme Int64)
    for col in INTEGER_COLUMNS:
        if col in df.columns:
            try:
                df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")
            except (ValueError, TypeError):
                pass  # Ponecháme původní typ
    
    # Konverze float sloupců pro numerické hodnoty
    float_candidates = [
        "Zeměpisná_délka", "Zeměpisná_šířka", "Nadmořská_výška",
        "Koncentrační _faktor", "Koncentrační_faktor",
        "Vzdálenost_od_budovy", "Vzdálenost_od_stromu",
        "Hloubka_odběru_vody", "Výška_odběru", "Výška_nádoby",
        "Objem_výpusti_a", "Objem_výpusti_b", "Objem_vzorku",
        "Hmotnost_prachu", "Hmotnost_spadu",
        "Velikost_plochy", "Hloubka_odběru_půdy_od", "Hloubka_odběru_půdy_do",
        "Množství", "Hodnota", "Nejistota", "Doba",
    ]
    
    for col in float_candidates:
        if col in df.columns:
            try:
                df[col] = pd.to_numeric(df[col], errors="coerce").astype("Float64")
            except (ValueError, TypeError):
                pass
    
    return df


def get_excel_info(file_path: str | Path) -> dict:
    """
    Získá informace o Excel souboru bez načtení celých dat.
    
    Args:
        file_path: Cesta k xlsx souboru
        
    Returns:
        Slovník s informacemi o souboru
    """
    file_path = Path(file_path)
    excel_file = pd.ExcelFile(file_path)
    
    info = {
        "file_name": file_path.name,
        "file_path": str(file_path),
        "sheets": [],
    }
    
    for sheet_name in excel_file.sheet_names:
        df = pd.read_excel(excel_file, sheet_name=sheet_name, nrows=0)
        sheet_info = {
            "name": sheet_name,
            "columns": list(df.columns),
            "column_count": len(df.columns),
            "is_data_sheet": sheet_name == find_data_sheet(excel_file),
        }
        info["sheets"].append(sheet_info)
    
    return info


if __name__ == "__main__":
    # Test modulu
    import sys
    
    if len(sys.argv) > 1:
        test_file = sys.argv[1]
    else:
        test_file = r"C:\Users\genie\Documents\Python\konzistence_monras\data\Polozky_PR\Smíšená strava 2023.xlsx"
    
    print(f"Načítám soubor: {test_file}")
    df = read_monras_excel(test_file)
    
    print(f"\nNačteno z listu: {df.attrs['sheet_name']}")
    print(f"Počet řádků: {len(df)}")
    print(f"Počet sloupců: {len(df.columns)}")
    print(f"\nDatové typy sloupců:")
    print(df.dtypes.to_string())
    print(f"\nPrvních 5 řádků:")
    print(df.head())
