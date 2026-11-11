"""Brand-to-generic drug dictionary.

Keys are lowercase brand names (as they appear on prescriptions).
Values are the generic name and (optionally) common strength hints.

Sources:
- Indian pharmacopoeia common brands (201calm, Clonelst, Vexidsp, etc.)
- Global brands (Betaloc, Lopressor, etc.)

Extend this list as new brands appear in real prescriptions.
"""

DRUG_DICT: dict[str, dict] = {
    # --- Anxiolytics / Antidepressants ---
    "201calm":       {"generic": "Etizolam",       "class": "anxiolytic"},
    "etizola":       {"generic": "Etizolam"},
    "clonelst":      {"generic": "Clonazepam",     "class": "benzodiazepine"},
    "clonotril":     {"generic": "Clonazepam",     "class": "benzodiazepine"},
    "rivotril":      {"generic": "Clonazepam",     "class": "benzodiazepine"},
    "alprax":        {"generic": "Alprazolam",     "class": "benzodiazepine"},
    "restyl":        {"generic": "Alprazolam",     "class": "benzodiazepine"},
    "nexito":        {"generic": "Escitalopram",   "class": "ssri"},
    "tryptomer":     {"generic": "Amitriptyline",  "class": "tca"},
    "serta":         {"generic": "Sertraline",     "class": "ssri"},

    # --- Beta-blockers ---
    "betaloc":       {"generic": "Metoprolol",     "class": "beta_blocker"},
    "lopressor":     {"generic": "Metoprolol",     "class": "beta_blocker"},
    "oxprelol":      {"generic": "Oxprenolol",     "class": "beta_blocker"},
    "tenormin":      {"generic": "Atenolol",       "class": "beta_blocker"},
    "aten":          {"generic": "Atenolol",       "class": "beta_blocker"},
    "inderal":       {"generic": "Propranolol",    "class": "beta_blocker"},
    "ciptin":        {"generic": "Propranolol",    "class": "beta_blocker"},

    # --- H2 blockers / PPIs ---
    "cimetidine":    {"generic": "Cimetidine",     "class": "h2_blocker"},
    "tagamet":       {"generic": "Cimetidine",     "class": "h2_blocker"},
    "rantac":        {"generic": "Ranitidine",     "class": "h2_blocker"},
    "zantac":        {"generic": "Ranitidine",     "class": "h2_blocker"},
    "omee":          {"generic": "Omeprazole",     "class": "ppi"},
    "omez":          {"generic": "Omeprazole",     "class": "ppi"},
    "pan":           {"generic": "Pantoprazole",   "class": "ppi"},
    "pantocid":      {"generic": "Pantoprazole",   "class": "ppi"},
    "rabium":        {"generic": "Rabeprazole",    "class": "ppi"},

    # --- Diabetes ---
    "glycomet":      {"generic": "Metformin",      "class": "biguanide"},
    "glucophage":    {"generic": "Metformin",      "class": "biguanide"},
    "januvia":       {"generic": "Sitagliptin",    "class": "dpp4"},
    "amaryl":        {"generic": "Glimepiride",    "class": "sulfonylurea"},
    "glimepiride":   {"generic": "Glimepiride",    "class": "sulfonylurea"},

    # --- Antihypertensives ---
    "amlokind":      {"generic": "Amlodipine",     "class": "ccb"},
    "amlopres":      {"generic": "Amlodipine",     "class": "ccb"},
    "telma":         {"generic": "Telmisartan",    "class": "arb"},
    "telvas":        {"generic": "Telmisartan",    "class": "arb"},
    "losar":         {"generic": "Losartan",       "class": "arb"},
    "enalap":        {"generic": "Enalapril",      "class": "ace_inhibitor"},
    "ramipril":      {"generic": "Ramipril",       "class": "ace_inhibitor"},

    # --- Statins ---
    "atorva":        {"generic": "Atorvastatin",   "class": "statin"},
    "lipitor":       {"generic": "Atorvastatin",   "class": "statin"},
    "rosuvas":       {"generic": "Rosuvastatin",   "class": "statin"},
    "crestor":       {"generic": "Rosuvastatin",   "class": "statin"},

    # --- Analgesics / Antipyretics ---
    "crocin":        {"generic": "Paracetamol",    "class": "analgesic"},
    "dolo":          {"generic": "Paracetamol",    "class": "analgesic"},
    "calpol":        {"generic": "Paracetamol",    "class": "analgesic"},
    "combiflam":     {"generic": "Ibuprofen+Paracetamol", "class": "analgesic"},
    "brufen":        {"generic": "Ibuprofen",      "class": "nsaid"},
    "voveran":       {"generic": "Diclofenac",     "class": "nsaid"},

    # --- Antibiotics ---
    "augmentin":     {"generic": "Amoxicillin+Clavulanate", "class": "antibiotic"},
    "azee":          {"generic": "Azithromycin",   "class": "antibiotic"},
    "azithral":      {"generic": "Azithromycin",   "class": "antibiotic"},
    "cipro":         {"generic": "Ciprofloxacin",  "class": "antibiotic"},
    "levoflox":      {"generic": "Levofloxacin",   "class": "antibiotic"},
    "monocef":       {"generic": "Ceftriaxone",    "class": "antibiotic"},

    # --- Antiallergics ---
    "allegra":       {"generic": "Fexofenadine",   "class": "antihistamine"},
    "cetzine":       {"generic": "Cetirizine",     "class": "antihistamine"},
    "levocet":       {"generic": "Levocetirizine", "class": "antihistamine"},
    "montair":       {"generic": "Montelukast",    "class": "antileukotriene"},

    # --- Miscellaneous ---
    "thyronorm":     {"generic": "Thyroxine",      "class": "hormone"},
    "eltroxin":      {"generic": "Thyroxine",      "class": "hormone"},
    "shelcal":       {"generic": "Calcium+Vitamin D3", "class": "supplement"},
    "neurobion":     {"generic": "Vitamin B Complex", "class": "supplement"},
    "supradyn":      {"generic": "Multivitamin",   "class": "supplement"},
}


def lookup(brand: str) -> dict | None:
    """Case-insensitive lookup. Returns dict with 'generic' and optional 'class'."""
    if not brand:
        return None
    return DRUG_DICT.get(brand.strip().lower())


def normalize_brand(brand: str) -> tuple[str, str | None, float]:
    """Return (generic_or_original, drug_class, confidence).

    If found:    confidence 0.95
    If not found: confidence 0.6  (keep brand, flag for review)
    """
    hit = lookup(brand)
    if hit:
        return hit["generic"], hit.get("class"), 0.95
    return brand, None, 0.6