from typing import Optional
import re
import warnings
import numpy as np
import pandas as pd

# Potlačení pandas varování
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=UserWarning, message='Could not infer format')
pd.set_option('future.no_silent_downcasting', True)

def _clean_missing(s: pd.Series) -> pd.Series:
    if s.dtype == object:
        result = s.replace(
            to_replace=[None, "", " ", "-", "\u2013", "\u2014", "NA", "N/A", "nan", "NaN"],
            value=np.nan,
        )
        return result
    return s

def _fix_wrong_year_in_string(s: pd.Series) -> pd.Series:
    """
    Opraví chybné roky ve stringových datetime hodnotách PŘED parsováním.
    
    Detekuje vzory jako:
    - "03.09.0016 22:57" -> "03.09.2016 22:57"
    - "28.07.0013 22:57" -> "28.07.2013 22:57"
    - "30.12.0011 22:54" -> "30.12.2011 22:54"
    
    Roky 0001-0099 se převedou na 2001-2099.
    """
    if s.dtype != object:
        return s
    
    result = s.copy()
    
    # Regex pro detekci datetime s chybným rokem (4 číslice začínající 00)
    # Formáty: DD.MM.00YY nebo 00YY-MM-DD
    pattern_dot = re.compile(r'(\d{1,2})\.(\d{1,2})\.(00)(\d{2})(\s|$|T)')  # DD.MM.00YY
    pattern_dash = re.compile(r'(00)(\d{2})-(\d{2})-(\d{2})(\s|$|T)')  # 00YY-MM-DD
    
    def fix_year(val):
        if pd.isna(val) or not isinstance(val, str):
            return val
        
        # Oprava formátu DD.MM.00YY
        match = pattern_dot.search(val)
        if match:
            day, month, _, year_suffix, rest = match.groups()
            new_year = f"20{year_suffix}"
            return pattern_dot.sub(rf'{day}.{month}.{new_year}{rest}', val)
        
        # Oprava formátu 00YY-MM-DD
        match = pattern_dash.search(val)
        if match:
            _, year_suffix, month, day, rest = match.groups()
            new_year = f"20{year_suffix}"
            return pattern_dash.sub(rf'{new_year}-{month}-{day}{rest}', val)
        
        return val
    
    mask = result.notna() & (result.astype(str).str.contains(r'\.00\d{2}\s|\.00\d{2}$|^00\d{2}-', regex=True, na=False))
    if mask.any():
        result.loc[mask] = result.loc[mask].apply(fix_year)
    
    return result

def _dt_from_excel_serial(s: pd.Series) -> pd.Series:
    x = pd.to_numeric(s, errors="coerce")
    # realistický rozsah excel serialů
    mask = x.between(20000, 80000)
    out = pd.Series(pd.NaT, index=s.index, dtype="datetime64[ns]")
    if mask.any():
        out.loc[mask] = pd.to_datetime(x.loc[mask], unit="D", origin="1899-12-30", errors="coerce")
    return out

def _fix_wrong_years(dt_series: pd.Series) -> pd.Series:
    """
    Opraví chybné roky v datetime series:
    - Roky < 100 (např. 0013, 0016) -> přičte 2000 (2013, 2016)
    - Roky mimo rozumný rozsah (např. < 1950 nebo > 2100) -> opraví pokud možné
    
    Tyto roky jsou evidentně překlepy v datech (2013 -> 0013, 2016 -> 0016).
    """
    if dt_series.isna().all():
        return dt_series
    
    result = dt_series.copy()
    years = dt_series.dt.year
    
    # Maska pro roky < 100 (např. 0013, 0016 atd.)
    wrong_year_mask = (years < 100) & dt_series.notna()
    
    if wrong_year_mask.any():
        def fix_small_year(x):
            if pd.isna(x):
                return x
            try:
                # Přidej 2000 k malým rokům (0013 -> 2013, 0016 -> 2016)
                return x.replace(year=x.year + 2000)
            except (ValueError, OverflowError):
                return pd.NaT
        
        corrected = dt_series[wrong_year_mask].apply(fix_small_year)
        result.loc[wrong_year_mask] = corrected
    
    # Maska pro roky mimo rozumný rozsah (1950-2100)
    # ale už ne < 100 (ty jsme opravili)
    years_updated = result.dt.year
    unreasonable_mask = (
        ((years_updated < 1950) | (years_updated > 2100)) & 
        result.notna() & 
        (years_updated >= 100)  # Neopravené malé roky
    )
    
    if unreasonable_mask.any():
        def try_fix_unreasonable(x):
            if pd.isna(x):
                return x
            year = x.year
            # Zkus odhadnout správný rok
            if 100 <= year < 1000:
                # Např. 201 -> 2001, 202 -> 2002
                try:
                    return x.replace(year=year + 1000)
                except (ValueError, OverflowError):
                    pass
            elif 1000 <= year < 1950:
                # Např. 1016 -> 2016
                if year < 1100:
                    try:
                        return x.replace(year=year + 1000)
                    except (ValueError, OverflowError):
                        pass
            # Pokud nic nefunguje, vrať NaT
            return pd.NaT
        
        corrected = result[unreasonable_mask].apply(try_fix_unreasonable)
        result.loc[unreasonable_mask] = corrected
    
    return result

def parse_datetime_series(series: pd.Series, assume_utc: bool) -> pd.Series:
    """
    Vrací:
      - assume_utc=True  -> datetime64[ns, UTC]
      - assume_utc=False -> datetime64[ns]
    """
    s = _clean_missing(series.copy())
    
    # 0) Oprava chybných roků ve stringových hodnotách PŘED parsováním
    #    (např. "03.09.0016 22:57" -> "03.09.2016 22:57")
    s = _fix_wrong_year_in_string(s)

    # 1) serialy
    dt_serial = _dt_from_excel_serial(s)

    # 2) přímý parsing (zvládá i Timestamp)
    dt1 = pd.to_datetime(s, errors="coerce", dayfirst=True, utc=assume_utc, format="mixed")

    # 3) fallback dayfirst=False pro zbylé
    need = dt1.isna()
    if need.any():
        dt2 = pd.to_datetime(s[need], errors="coerce", dayfirst=False, utc=assume_utc, format="mixed")
        dt1.loc[need] = dt2

    # 4) doplnění serialů tam, kde parsing selhal
    need2 = dt1.isna() & dt_serial.notna()
    if need2.any():
        if assume_utc:
            dt_serial_utc = dt_serial.dt.tz_localize("UTC", nonexistent="NaT", ambiguous="NaT")
            dt1.loc[need2] = dt_serial_utc.loc[need2]
        else:
            dt1.loc[need2] = dt_serial.loc[need2]

    # 5) Oprava chybných roků v již zparsovaných datetime (záloha)
    dt1 = _fix_wrong_years(dt1)

    # 6) tz-naive režim
    if not assume_utc:
        if getattr(dt1.dtype, "tz", None) is not None:
            dt1 = dt1.dt.tz_convert(None)
        dt1 = pd.to_datetime(dt1, errors="coerce")

    return dt1

def detect_datetime_columns(cols, detect_regex: str):
    pat = re.compile(detect_regex, re.IGNORECASE)
    return [c for c in cols if pat.search(str(c))]

def is_utc_column(col: str, utc_regex: str) -> bool:
    return re.search(utc_regex, str(col), flags=re.IGNORECASE) is not None

def datetime_to_storage(series: pd.Series,
                        assume_utc: bool,
                        store_as: str,
                        iso_format_naive: str,
                        iso_format_utc: str) -> pd.Series:
    """
    Převod datetime na hodnoty vhodné pro SQLite.
    - iso_text: TEXT (ISO)
    - unix_ms: INTEGER (epoch ms)
    """
    if store_as == "unix_ms":
        if assume_utc:
            # tz-aware UTC
            s = series
            # pandas: astype('int64') je ns; převedeme na ms
            out = pd.Series(pd.NA, index=s.index, dtype="Int64")
            ok = s.notna()
            if ok.any():
                out.loc[ok] = (s.loc[ok].astype("int64") // 1_000_000).astype("Int64")
            return out
        else:
            # tz-naive interpretujeme jako "lokální", ale do epoch ms bez zóny nedává smysl.
            # Přesto: bereme jako naive UTC-like; pokud nechcete, nastavte store_as=iso_text.
            s = series
            out = pd.Series(pd.NA, index=s.index, dtype="Int64")
            ok = s.notna()
            if ok.any():
                out.loc[ok] = (s.loc[ok].astype("int64") // 1_000_000).astype("Int64")
            return out

    # default iso_text
    if assume_utc:
        return series.dt.strftime(iso_format_utc)
    return series.dt.strftime(iso_format_naive)
