# Inventory Valuation

A Python command-line program that compares inventory data with a price list
and creates valuation reports.

## Requirements

- Python 3.10 or newer
- Dependencies are in `requirements.txt`

## Install

Clone the repository and enter the repository folder:

```bash
git clone <repository-url>
cd inventory_valuation
```

Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

On Windows:

```bash
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Run

Run this command from the repository root:

```bash
python -m inventory_valuation --inventory data/inventory.csv --prices data/prices.csv --out-dir output
```

Use `--help` to view available options:

```bash
python -m inventory_valuation --help
```

## Output

The program creates:

- `inventory_valuation_report.csv`
- `problem_items.csv`
- `inventory_valuation_report.xlsx` when `openpyxl` is installed
