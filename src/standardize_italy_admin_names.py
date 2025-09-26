# standardize_italy_admin_names.py
# Clean/standardize Italian provinces, regions, macro-areas. Compact + robust.

import re
import unicodedata
from difflib import get_close_matches

# Import all canonical dictionaries/mappings
from aliases_helper import (
    REGIONS,
    REGION_TO_PROVINCES,
    PROVINCE_TO_REGION,
    MACRO_TO_REGIONS,
    REGION_TO_MACRO,
    METRO_CITIES,
    CANONICAL_TO_ALIASES,
)

# ---------- Normalization helpers (used everywhere) ----------

def strip_accents(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))

def base_normalize(s: str) -> str:
    s = strip_accents(str(s).lower().strip())
    s = re.sub(r"[’'`]", " ", s)
    s = re.sub(r"[-–—]", " ", s)
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"^(provincia di|prov di|citta metropolitana di)\s+", "", s)
    return s.strip()

def match_from_candidates(token: str, candidates):
    hits = get_close_matches(token, candidates, n=1, cutoff=0.90)
    return hits[0] if hits else None

# ---------- Build alias map (concise + auto-variants) ----------

ALL_REGIONS   = list(REGION_TO_PROVINCES.keys())
ALL_PROVINCES = sorted({p for ps in REGION_TO_PROVINCES.values() for p in ps})
MACROS        = sorted(MACRO_TO_REGIONS.keys())

def auto_variants_for_province(name: str):
    """Generate common forms: 'provincia di ...', metro forms, etc."""
    b = base_normalize(name)
    out = {b, f"provincia di {b}", f"prov di {b}"}
    if name in METRO_CITIES:
        out.add(f"citta metropolitana di {b}")
    return out

def build_alias_map():
    """
    normalized_alias -> CanonicalName
    Includes:
      - canonical self-keys,
      - auto-variants for provinces,
      - manual ambiguous variants.
    """
    aliases = {}

    # Canonical exacts
    for r in ALL_REGIONS:
        aliases[base_normalize(r)] = r
    for p in ALL_PROVINCES:
        aliases[base_normalize(p)] = p
    for m in MACROS:
        aliases[base_normalize(m)] = m

    # Auto-variants for provinces
    for p in ALL_PROVINCES:
        for a in auto_variants_for_province(p):
            aliases[base_normalize(a)] = p

    # Manual groups
    for canonical, variants in CANONICAL_TO_ALIASES.items():
        for a in variants:
            aliases[base_normalize(a)] = canonical

    return aliases

ALIASES = build_alias_map()

# Precompute normalized lookups
NORM_PROV  = {base_normalize(k): k for k in PROVINCE_TO_REGION.keys()}
NORM_REG   = {base_normalize(k): k for k in REGIONS}
NORM_MAC   = {base_normalize(k): k for k in MACROS}
# ALIASES already has normalized keys, but keep the same access pattern:
NORM_ALIAS = ALIASES

# ---------- Core standardizer ----------

def standardize_territory(raw: str):
    """
    Input: raw label (province/region/macro, possibly messy)
    Output dict:
      level: 'province' | 'region' | 'macro' | 'unknown'
      province_std, region_std, macro_std
    """
    if raw is None:
        return {"level":"unknown","province_std":None,"region_std":None,"macro_std":None}

    tok = base_normalize(raw)

    # 1) Alias pass (fast exact on normalized)
    if tok in NORM_ALIAS:
        canonical = NORM_ALIAS[tok]
        if canonical in PROVINCE_TO_REGION:
            reg = PROVINCE_TO_REGION[canonical]
            return {"level":"province","province_std":canonical,"region_std":reg,"macro_std":REGION_TO_MACRO[reg]}
        if canonical in REGIONS:
            reg = canonical
            return {"level":"region","province_std":None,"region_std":reg,"macro_std":REGION_TO_MACRO[reg]}
        if canonical in MACROS:
            return {"level":"macro","province_std":None,"region_std":None,"macro_std":canonical}

    # 2) Direct exact on normalized
    if tok in NORM_PROV:
        p = NORM_PROV[tok]; r = PROVINCE_TO_REGION[p]
        return {"level":"province","province_std":p,"region_std":r,"macro_std":REGION_TO_MACRO[r]}
    if tok in NORM_REG:
        r = NORM_REG[tok]
        return {"level":"region","province_std":None,"region_std":r,"macro_std":REGION_TO_MACRO[r]}
    if tok in NORM_MAC:
        return {"level":"macro","province_std":None,"region_std":None,"macro_std":NORM_MAC[tok]}

    # 3) Fallback close-match
    m = match_from_candidates(tok, list(NORM_PROV.keys()))
    if m:
        p = NORM_PROV[m]; r = PROVINCE_TO_REGION[p]
        return {"level":"province","province_std":p,"region_std":r,"macro_std":REGION_TO_MACRO[r]}
    m = match_from_candidates(tok, list(NORM_REG.keys()))
    if m:
        r = NORM_REG[m]
        return {"level":"region","province_std":None,"region_std":r,"macro_std":REGION_TO_MACRO[r]}
    m = match_from_candidates(tok, list(NORM_MAC.keys()))
    if m:
        return {"level":"macro","province_std":None,"region_std":None,"macro_std":NORM_MAC[m]}

    # 4) Last-resort heuristic (Aosta variants)
    if "aosta" in tok:
        return {"level":"region","province_std":None,"region_std":"Valle d'Aosta/Vallée d'Aoste","macro_std":"Nord-ovest"}

    return {"level":"unknown","province_std":None,"region_std":None,"macro_std":None}

# ---------- Optional: vectorized usage with pandas ----------
# import pandas as pd
# df = ...  # has a column 'territory' or 'province'
# out = df["territory"].apply(standardize_territory).apply(pd.Series)
# df = pd.concat([df, out], axis=1)
