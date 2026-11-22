import re
import unicodedata


KNOWN_PRODUCT_TYPES: tuple[str, ...] = (
    "collector booster display",
    "play booster display",
    "elite trainer box",
    "booster display",
    "booster bundle",
    "special box",
    "starter deck",
    "bundle",
)


def normalize_language(raw: str | None) -> str:
    if not raw:
        return ""
    val = raw.strip().lower()
    if val in {"en", "eng", "english", "englisch"}:
        return "EN"
    if val in {"de", "german", "deutsch"}:
        return "DE"
    return val.upper()


def normalize_text(raw: str | None) -> str:
    if not raw:
        return ""
    text = unicodedata.normalize("NFKC", raw).strip().lower()
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"^pokémon\s+tcg:\s*", "pokémon ", text)
    text = re.sub(r"^mtg\b", "magic the gathering", text)
    text = re.sub(r"^magic:\s*the\s+gathering\s*-\s*", "magic the gathering ", text)
    text = re.sub(r"^magic:\s*the\s+gathering\s+", "magic the gathering ", text)
    text = re.sub(r"\bplay\s+booster\s+box\b", "play booster display", text)
    text = re.sub(r"[^\w\s]", "", text)
    return re.sub(r"\s+", " ", text).strip()


def derive_set_and_type(norm_name: str) -> tuple[str, str]:
    for ptype in KNOWN_PRODUCT_TYPES:
        if norm_name.endswith(" " + ptype):
            return norm_name[: -len(ptype)].strip(), ptype
        if norm_name == ptype:
            return "", ptype
    return norm_name, ""


def parse_number(raw: str | None) -> float | None:
    if raw is None or not str(raw).strip():
        return None
    cleaned = re.sub(r"[€$£\s]", "", str(raw).strip())
    if "," in cleaned and "." in cleaned:
        if cleaned.rfind(",") > cleaned.rfind("."):
            cleaned = cleaned.replace(".", "").replace(",", ".")
        else:
            cleaned = cleaned.replace(",", "")
    elif "," in cleaned:
        cleaned = cleaned.replace(",", ".")
    try:
        return float(cleaned)
    except ValueError:
        return None


def format_de_number(val: float | None, decimals: int = 2) -> str:
    if val is None:
        return ""
    if decimals == 0 and val.is_integer():
        return str(int(val))
    return f"{val:.{decimals}f}".replace(".", ",")
