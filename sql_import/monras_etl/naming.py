import os
import re
import unicodedata

def slugify_identifier(s: str, max_len: int = 64) -> str:
    s = "" if s is None else str(s)
    s = s.replace("\r", " ").replace("\n", " ").strip()

    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = s.lower()

    s = re.sub(r"[^a-z0-9]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")

    if not s:
        s = "col"
    if re.match(r"^\d", s):
        s = f"c_{s}"

    return s[:max_len]

def table_name_from_filename(path: str,
                             drop_years: bool,
                             drop_trailing_version_suffix: bool,
                             keep_max_words: int,
                             max_len: int) -> str:
    base = os.path.splitext(os.path.basename(path))[0]
    s = base

    if drop_trailing_version_suffix:
        # odstraní koncové _2, (2), -2 apod.
        s = re.sub(r"[_\-\s]*\(?\d+\)?\s*$", "", s)

    if drop_years:
        # odstraní rok na konci a případně i uvnitř názvu
        s = re.sub(r"[_\-\s]*(19\d{2}|20\d{2})\s*$", "", s)
        s = re.sub(r"\b(19\d{2}|20\d{2})\b", "", s)

    s = re.sub(r"\s+", " ", s).strip()

    words = s.split()
    if keep_max_words and len(words) > keep_max_words:
        s = " ".join(words[:keep_max_words])

    t = slugify_identifier(s, max_len=max_len)
    return t or "tabulka"
