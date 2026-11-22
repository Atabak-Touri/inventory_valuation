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
On Mac:
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

## How I worked

I started by looking at both files and writing down the errors I could see. such as duplicate rows, missing quantity, inconsistent language labels, extra spaces, capital letters, and different product naming between the two files. Then I reused ideas and code from my university case study and big data courses and combined them into one program, using GitHub Copilot in VS Code. I also used Claude to talk through the approach, review my code, and draft parts of this README.

## Assumptions

**Duplicates.** Two rows (INV-006 and INV-031) appear twice with exactly the same
content. I treated them as double entries and counted them once. If the same item
number had different content, the program does not choose; it flags both rows and
does not value them.

**Missing quantity.** INV-018 has no quantity. I did not assume 0. The item stays in the report without a value and is listed as a problem.

**Language.** The language column has many spellings (EN, en, English, Englisch, DE,
Deutsch, German, de). I map them all to EN or DE. The same product can have a very
different price in German and in English, so the language has to match. If a product
only exists in the other language, I still show that price, but I mark the item as
doubtful and keep it out of the confirmed total. The report shows both totals.

**Product type.** Booster Display, Special Box and so on are different products with
different prices, so the type has to match too. INV-054 (One Piece Crimson Tide
Booster Display) has no entry in the price list; there is only a Starter Deck for
that set. I did not use the Starter Deck price, so the item is listed as unmatched
without a value.

**Names.** I ignore capital letters and extra spaces. "MTG" is read as "Magic: The
Gathering", and the "Pokémon TCG:" prefix and the dash used in the price list are
removed. "Play Booster Box" is read as "Play Booster Display", because the inventory's own product type column and the price list both say Display. I did not use fuzzy matching, so anything these rules do not cover shows up as unmatched and is not guessed.

**Condition.** Items marked "box damaged" are valued at the same price as sealed ones. They are marked in the notes column. Their real value is probably lower, so the total may be a bit too high.

**Prices.** Each item's value is rounded to two decimals before the values are added up.

**Files.** The inventory file is seperated by comma and the price file is seperated by semicolon.
