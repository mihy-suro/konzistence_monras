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
    Opraví chybné roky < 100 (např. 0013, 0016) přičtením 2000.
    Tyto roky jsou evidentně překlepy v datech (2013 -> 0013).
    """
    if dt_series.isna().all():
        return dt_series
    
    # Detekuj roky < 100
    years = dt_series.dt.year
    wrong_year_mask = (years < 100) & dt_series.notna()
    
    if not wrong_year_mask.any():
        return dt_series
    
    # Oprav roky přičtením 2000
    result = dt_series.copy()
    if wrong_year_mask.any():
        # Pro tz-aware datetimes
        if hasattr(dt_series.dt, 'tz') and dt_series.dt.tz is not None:
            corrected = dt_series[wrong_year_mask].apply(
                lambda x: x.replace(year=x.year + 2000) if pd.notna(x) else x
            )
        else:
            corrected = dt_series[wrong_year_mask].apply(
                lambda x: x.replace(year=x.year + 2000) if pd.notna(x) else x
            )
        result.loc[wrong_year_mask] = corrected
    
    return result

def parse_datetime_series(series: pd.Series, assume_utc: bool) -> pd.Series:
    """
    Vrací:
      - assume_utc=True  -> datetime64[ns, UTC]
      - assume_utc=False -> datetime64[ns]
    """
    s = _clean_missing(series.copy())

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

    # 5) tz-naive režim
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
