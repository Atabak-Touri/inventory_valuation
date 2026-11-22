from pathlib import Path

from .csv_utils import read_csv_fixed
from .models import PriceRecord
from .text_utils import derive_set_and_type, normalize_language, normalize_text, parse_number


def load_prices(
    filepath: Path,
) -> tuple[dict[tuple[str, str, str], PriceRecord], dict[tuple[str, str], list[PriceRecord]], int]:
    rows = read_csv_fixed(filepath, delimiter=";")
    exact_index: dict[tuple[str, str, str], PriceRecord] = {}
    type_index: dict[tuple[str, str], list[PriceRecord]] = {}
    skipped_invalid_prices = 0

    for row_num, r in enumerate(rows, start=2):
        avg_val = parse_number(r.get("avg_price_eur"))
        if avg_val is None:
            skipped_invalid_prices += 1
            continue

        low_val = parse_number(r.get("low_price_eur"))
        norm_name = normalize_text(r.get("name", ""))
        set_name, derived_type = derive_set_and_type(norm_name)
        lang = normalize_language(r.get("language", ""))
        product_id = r.get("product_id", "")

        key = (set_name, derived_type, lang)
        if key in exact_index:
            existing = exact_index[key]
            raise ValueError(
                f"Duplicate price key {key} in {filepath} at row {row_num}: "
                f"'{product_id}' conflicts with existing '{existing.product_id}'."
            )

        rec = PriceRecord(
            product_id=product_id,
            raw_name=r.get("name", ""),
            set_name=set_name,
            derived_type=derived_type,
            language=lang,
            avg_price_eur=avg_val,
            low_price_eur=low_val,
            date=r.get("date", ""),
        )
        exact_index[key] = rec
        type_index.setdefault((set_name, derived_type), []).append(rec)

    return exact_index, type_index, skipped_invalid_prices
