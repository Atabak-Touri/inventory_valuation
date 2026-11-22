from dataclasses import dataclass


@dataclass
class PriceRecord:
    product_id: str
    raw_name: str
    set_name: str
    derived_type: str
    language: str
    avg_price_eur: float
    low_price_eur: float | None
    date: str


@dataclass
class ValuationResult:
    item_no: str
    product_name: str
    game: str
    raw_language: str
    norm_language: str
    derived_type: str
    quantity: float | None
    condition: str
    status: str
    matched_product_id: str
    matched_name: str
    matched_language: str
    avg_price_eur: float | None
    confirmed_value_eur: float | None
    doubtful_value_eur: float | None
    notes: str
