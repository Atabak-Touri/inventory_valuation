import csv
from pathlib import Path
from typing import Any

from .models import ValuationResult
from .text_utils import format_de_number

try:
    import openpyxl
    from openpyxl.styles import Font, PatternFill
    HAS_OPENPYXL = True
except ImportError:
    HAS_OPENPYXL = False


HEADERS = [
    "item_no",
    "product_name",
    "game",
    "raw_language",
    "norm_language",
    "derived_type",
    "quantity",
    "condition",
    "status",
    "matched_product_id",
    "matched_name",
    "matched_language",
    "avg_price_eur",
    "confirmed_value_eur",
    "doubtful_value_eur",
    "notes",
]


def to_csv_row(r: ValuationResult) -> list[str]:
    return [
        r.item_no,
        r.product_name,
        r.game,
        r.raw_language,
        r.norm_language,
        r.derived_type,
        format_de_number(r.quantity, decimals=0),
        r.condition,
        r.status,
        r.matched_product_id,
        r.matched_name,
        r.matched_language,
        format_de_number(r.avg_price_eur, decimals=2),
        format_de_number(r.confirmed_value_eur, decimals=2),
        format_de_number(r.doubtful_value_eur, decimals=2),
        r.notes,
    ]


def to_xlsx_row(r: ValuationResult) -> list[Any]:
    return [
        r.item_no,
        r.product_name,
        r.game,
        r.raw_language,
        r.norm_language,
        r.derived_type,
        int(r.quantity) if (r.quantity is not None and r.quantity.is_integer()) else r.quantity,
        r.condition,
        r.status,
        r.matched_product_id,
        r.matched_name,
        r.matched_language,
        r.avg_price_eur,
        r.confirmed_value_eur,
        r.doubtful_value_eur,
        r.notes,
    ]


def export_outputs(
    results: list[ValuationResult],
    confirmed_total: float,
    doubtful_total: float,
    out_dir: Path,
) -> tuple[Path, Path, Path | None]:
    out_dir.mkdir(parents=True, exist_ok=True)
    csv_path = out_dir / "inventory_valuation_report.csv"
    problems_csv_path = out_dir / "problem_items.csv"
    xlsx_path = out_dir / "inventory_valuation_report.xlsx"

    problem_rows = [r for r in results if r.status != "exact"]

    with csv_path.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(HEADERS)
        for r in results:
            w.writerow(to_csv_row(r))

    with problems_csv_path.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(HEADERS)
        for r in problem_rows:
            w.writerow(to_csv_row(r))

    if not HAS_OPENPYXL:
        print("WARNING: openpyxl is not installed; skipping .xlsx generation (CSV files were written).")
        return csv_path, problems_csv_path, None

    combined_total = round(confirmed_total + doubtful_total, 2)
    wb = openpyxl.Workbook()
    ws_all = wb.active
    ws_all.title = "Inventory Valuation"
    ws_all.append(HEADERS)
    for cell in ws_all[1]:
        cell.font = Font(bold=True)

    warn_fill = PatternFill(start_color="FFF2CC", end_color="FFF2CC", fill_type="solid")
    err_fill = PatternFill(start_color="FCE4D6", end_color="FCE4D6", fill_type="solid")

    for r in results:
        ws_all.append(to_xlsx_row(r))
        cells = ws_all[ws_all.max_row]
        if r.status in {"unmatched", "missing_quantity", "duplicate_conflict", "ambiguous"}:
            for c in cells:
                c.fill = err_fill
        elif r.status == "doubtful":
            for c in cells:
                c.fill = warn_fill

    ws_all.append([])
    ws_all.append(["Confirmed Total (EUR)", confirmed_total])
    ws_all.append(["Doubtful Total (EUR)", doubtful_total])
    ws_all.append(["Confirmed + Doubtful Total (EUR)", combined_total])

    ws_prob = wb.create_sheet("Problem Items")
    ws_prob.append(HEADERS)
    for cell in ws_prob[1]:
        cell.font = Font(bold=True)
    for r in problem_rows:
        ws_prob.append(to_xlsx_row(r))

    wb.save(xlsx_path)
    return csv_path, problems_csv_path, xlsx_path
