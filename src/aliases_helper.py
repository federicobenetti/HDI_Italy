# aliases_helper.py
# Canonical dictionaries & mappings for Italian admin units (no external deps).

# ---- Canonical lists ----
REGIONS = [
    "Abruzzo","Basilicata","Calabria","Campania","Emilia-Romagna","Friuli-Venezia Giulia",
    "Lazio","Liguria","Lombardia","Marche","Molise","Piemonte","Puglia","Sardegna",
    "Sicilia","Toscana","Trentino-Alto Adige/Südtirol","Umbria","Valle d'Aosta/Vallée d'Aoste","Veneto"
]

# ---- Region → Provinces (current assetto; update Sardegna if you adopt 2025 changes) ----
REGION_TO_PROVINCES = {
    "Abruzzo": ["L'Aquila","Teramo","Pescara","Chieti"],
    "Basilicata": ["Potenza","Matera"],
    "Calabria": ["Catanzaro","Cosenza","Crotone","Reggio Calabria","Vibo Valentia"],
    "Campania": ["Avellino","Benevento","Caserta","Napoli","Salerno"],
    "Emilia-Romagna": ["Bologna","Ferrara","Forlì-Cesena","Modena","Parma","Piacenza","Ravenna","Reggio nell'Emilia","Rimini"],
    "Friuli-Venezia Giulia": ["Gorizia","Pordenone","Trieste","Udine"],
    "Lazio": ["Frosinone","Latina","Rieti","Roma","Viterbo"],
    "Liguria": ["Genova","Imperia","La Spezia","Savona"],
    "Lombardia": ["Bergamo","Brescia","Como","Cremona","Lecco","Lodi","Mantova","Milano","Monza e della Brianza","Pavia","Sondrio","Varese"],
    "Marche": ["Ancona","Ascoli Piceno","Fermo","Macerata","Pesaro e Urbino"],
    "Molise": ["Campobasso","Isernia"],
    "Piemonte": ["Alessandria","Asti","Biella","Cuneo","Novara","Torino","Verbano-Cusio-Ossola","Vercelli"],
    "Puglia": ["Bari","Barletta-Andria-Trani","Brindisi","Foggia","Lecce","Taranto"],
    "Sardegna": ["Cagliari","Nuoro","Oristano","Sassari","Sud Sardegna"],
    "Sicilia": ["Agrigento","Caltanissetta","Catania","Enna","Messina","Palermo","Ragusa","Siracusa","Trapani"],
    "Toscana": ["Arezzo","Firenze","Grosseto","Livorno","Lucca","Massa-Carrara","Pisa","Pistoia","Prato","Siena"],
    "Trentino-Alto Adige/Südtirol": ["Bolzano/Bozen","Trento"],
    "Umbria": ["Perugia","Terni"],
    "Valle d'Aosta/Vallée d'Aoste": ["Aosta"],
    "Veneto": ["Belluno","Padova","Rovigo","Treviso","Venezia","Verona","Vicenza"],
}

# ---- Province → Region (derived) ----
PROVINCE_TO_REGION = {
    prov: region
    for region, provs in REGION_TO_PROVINCES.items()
    for prov in provs
}

# ---- ISTAT macro-areas ----
MACRO_TO_REGIONS = {
    "Nord-ovest": ["Piemonte", "Valle d'Aosta/Vallée d'Aoste", "Liguria", "Lombardia"],
    "Nord-est":   ["Trentino-Alto Adige/Südtirol", "Veneto", "Friuli-Venezia Giulia", "Emilia-Romagna"],
    "Centro":     ["Toscana", "Umbria", "Marche", "Lazio"],
    "Sud":        ["Abruzzo", "Molise", "Campania", "Puglia", "Basilicata", "Calabria"],
    "Isole":      ["Sicilia", "Sardegna"],
}

# ---- Region → Macro (derived) ----
REGION_TO_MACRO = {
    region: macro
    for macro, regions in MACRO_TO_REGIONS.items()
    for region in regions
}

# ---- Metro cities (to auto-generate common alias forms) ----
METRO_CITIES = {
    "Torino","Milano","Venezia","Genova","Bologna","Firenze","Roma","Napoli","Bari","Reggio Calabria",
    "Cagliari","Catania","Messina","Palermo"
}

# ---- Manual alias groups (only truly ambiguous/common variants) ----
CANONICAL_TO_ALIASES = {
    # Provinces
    "Reggio nell'Emilia": ["reggio emilia"],
    "Reggio Calabria": ["reggio di calabria"],
    "Forlì-Cesena": ["forli cesena","forli-cesena","forlì cesena"],
    "La Spezia": ["spezia"],
    "Massa-Carrara": ["massa carrara","massa-carrara"],
    "Monza e della Brianza": ["monza e brianza","monza brianza"],
    "Bolzano/Bozen": ["bolzano","bozen","bolzano-bozen","bozen-bolzano"],
    "Barletta-Andria-Trani": ["barletta andria trani","bat","b.a.t."],
    "Pesaro e Urbino": ["pesaro urbino"],
    "Valle d'Aosta/Vallée d'Aoste": ["valle d aosta","valle d'aosta","valle d’aosta","vallee daoste"],
    # Regions
    "Friuli-Venezia Giulia": ["friuli venezia giulia"],
    "Trentino-Alto Adige/Südtirol": ["trentino alto adige","trentino-alto adige"],
}

__all__ = [
    "REGIONS",
    "REGION_TO_PROVINCES",
    "PROVINCE_TO_REGION",
    "MACRO_TO_REGIONS",
    "REGION_TO_MACRO",
    "METRO_CITIES",
    "CANONICAL_TO_ALIASES",
]
