import argparse
from pathlib import Path

from .export import export_outputs
from .inventory import evaluate_inventory
from .pricing import load_prices


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Reconcile stock inventory against a price list and export valuation reports."
    )
    parser.add_argument(
        "--inventory",
        type=Path,
        default=Path("data/inventory.csv"),
        help="Path to the inventory CSV file (default: data/inventory.csv)",
    )
    parser.add_argument(
        "--prices",
        type=Path,
        default=Path("data/prices.csv"),
        help="Path to the prices CSV file (default: data/prices.csv)",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("output"),
        help="Directory where output files will be written (default: output)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    exact_index, type_index, skipped_prices = load_prices(args.prices)
    results, confirmed_total, doubtful_total, dropped_dups, conflict_ids = evaluate_inventory(
        args.inventory, exact_index, type_index
    )
    csv_path, problems_path, xlsx_path = export_outputs(
        results, confirmed_total, doubtful_total, args.out_dir
    )

    print(f"Skipped invalid price rows : {skipped_prices}")
    print(f"Dropped exact duplicates   : {len(dropped_dups)}" + (f" ({', '.join(dropped_dups)})" if dropped_dups else ""))
    if conflict_ids:
        print(f"WARNING - Conflicting IDs  : {', '.join(conflict_ids)}")
    print(f"Unique items processed     : {len(results)}")
    print(f"Exact matches (priced)     : {sum(1 for r in results if r.status == 'exact')}")
    print(f"Missing quantity           : {sum(1 for r in results if r.status == 'missing_quantity')}")
    print(f"Doubtful (cross-language)  : {sum(1 for r in results if r.status == 'doubtful')}")
    print(f"Ambiguous fallbacks        : {sum(1 for r in results if r.status == 'ambiguous')}")
    print(f"Unmatched                  : {sum(1 for r in results if r.status == 'unmatched')}")
    print(f"Confirmed Total            : {confirmed_total:,.2f} EUR")
    print(f"Confirmed + Doubtful Total : {confirmed_total + doubtful_total:,.2f} EUR")
    print(f"Written CSV                : {csv_path}")
    print(f"Written Problem CSV        : {problems_path}")
    if xlsx_path:
        print(f"Written Excel              : {xlsx_path}")
