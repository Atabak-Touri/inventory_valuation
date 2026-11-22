import csv
from pathlib import Path


def read_csv_fixed(filepath: Path, delimiter: str) -> list[dict[str, str]]:
    if not filepath.exists():
        raise FileNotFoundError(f"Input file not found: {filepath}")

    raw_bytes = filepath.read_bytes()
    text = None
    for enc in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
        try:
            text = raw_bytes.decode(enc)
            break
        except UnicodeDecodeError:
            continue
    if text is None:
        raise ValueError(f"Unable to decode {filepath} with supported encodings.")

    lines = [line for line in text.splitlines() if line.strip()]
    reader = csv.DictReader(lines, delimiter=delimiter)
    return [
        {k.strip().lower(): (v.strip() if v is not None else "") for k, v in row.items()}
        for row in reader
    ]
