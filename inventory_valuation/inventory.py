import re
from pathlib import Path

from .csv_utils import read_csv_fixed
from .models import PriceRecord, ValuationResult
from .text_utils import derive_set_and_type, normalize_language, normalize_text, parse_number


def deduplicate_inventory(
    raw_rows: list[dict[str, str]],
) -> tuple[list[tuple[dict[str, str], bool]], list[str], list[str]]:
    grouped: dict[str, list[dict[str, str]]] = {}
    order: list[str] = []

    for idx, row in enumerate(raw_rows):
        norm_id = row.get("item_no", "").strip().upper() or f"__NO_ID_ROW_{idx}__"
        if norm_id not in grouped:
            grouped[norm_id] = []
            order.append(norm_id)
        grouped[norm_id].append(row)

    cleaned_rows: list[tuple[dict[str, str], bool]] = []
    dropped_duplicates: list[str] = []
    conflict_ids: list[str] = []

    for norm_id in order:
        group = grouped[norm_id]
        if len(group) == 1:
            cleaned_rows.append((group[0], False))
            continue

        signatures = {
            tuple((k, re.sub(r"\s+", " ", v).strip()) for k, v in sorted(r.items()))
            for r in group
        }
        if len(signatures) == 1:
            cleaned_rows.append((group[0], False))
            dropped_duplicates.extend([norm_id] * (len(group) - 1))
        else:
            conflict_ids.append(norm_id)
            for r in group:
                cleaned_rows.append((r, True))

    return cleaned_rows, dropped_duplicates, conflict_ids


def evaluate_inventory(
    filepath: Path,
    exact_index: dict[tuple[str, str, str], PriceRecord],
    type_index: dict[tuple[str, str], list[PriceRecord]],
) -> tuple[list[ValuationResult], float, float, list[str], list[str]]:
    raw_rows = read_csv_fixed(filepath, delimiter=",")
    cleaned_rows, dropped_duplicates, conflict_ids = deduplicate_inventory(raw_rows)

    results: list[ValuationResult] = []
    confirmed_total = 0.0
    doubtful_total = 0.0

    for r, is_conflict in cleaned_rows:
        item_no = r.get("item_no", "").strip().upper()
        raw_name = r.get("product_name", "")
        game = r.get("game", "")
        raw_lang = r.get("language", "")
        raw_qty = r.get("quantity", "")
        condition = r.get("condition", "").lower()

        norm_lang = normalize_language(raw_lang)
        norm_name = normalize_text(raw_name)
        set_name, derived_type = derive_set_and_type(norm_name)

        if not derived_type and r.get("product_type"):
            derived_type = normalize_text(r.get("product_type"))

        qty_val = parse_number(raw_qty)
        notes: list[str] = []
        matched: PriceRecord | None = None

        if is_conflict:
            status = "duplicate_conflict"
            notes.append(f"conflicting duplicate rows for item_no '{item_no}'")
        else:
            exact_key = (set_name, derived_type, norm_lang)
            if exact_key in exact_index:
                matched = exact_index[exact_key]
                if qty_val is None:
                    status = "missing_quantity"
                    notes.append("missing quantity")
                else:
                    status = "exact"
            else:
                other_lang_candidates = type_index.get((set_name, derived_type), [])
                if len(other_lang_candidates) == 1:
                    matched = other_lang_candidates[0]
                    status = "doubtful"
                    notes.append(
                        f"cross-language match: inventory is {norm_lang}, priced using {matched.language} ({matched.product_id})"
                    )
                elif len(other_lang_candidates) > 1:
                    status = "ambiguous"
                    cand_desc = ", ".join(
                        f"{c.product_id} ({c.language}: {c.avg_price_eur:.2f})"
                        for c in other_lang_candidates
                    )
                    notes.append(f"ambiguous cross-language fallback: multiple candidates [{cand_desc}]")
                else:
                    status = "unmatched"
                    notes.append(f"no product match in prices.csv for '{set_name}' ({derived_type})")

        if condition == "box damaged":
            notes.append("box damaged")

        confirmed_val: float | None = None
        doubtful_val: float | None = None

        if matched and qty_val is not None and not is_conflict:
            line_total = round(qty_val * matched.avg_price_eur, 2)
            if status == "exact":
                confirmed_val = line_total
                confirmed_total += line_total
            elif status == "doubtful":
                doubtful_val = line_total
                doubtful_total += line_total

        results.append(
            ValuationResult(
                item_no=item_no,
                product_name=re.sub(r"\s+", " ", raw_name).strip(),
                game=game,
                raw_language=raw_lang,
                norm_language=norm_lang,
                derived_type=derived_type,
                quantity=qty_val,
                condition=condition,
                status=status,
                matched_product_id=matched.product_id if matched else "",
                matched_name=matched.raw_name if matched else "",
                matched_language=matched.language if matched else "",
                avg_price_eur=matched.avg_price_eur if matched else None,
                confirmed_value_eur=confirmed_val,
                doubtful_value_eur=doubtful_val,
                notes="; ".join(notes),
            )
        )

    return results, round(confirmed_total, 2), round(doubtful_total, 2), dropped_duplicates, conflict_ids
