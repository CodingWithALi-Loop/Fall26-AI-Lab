from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_MENU_CSV = BASE_DIR / "data" / "menu_updated.csv"
FALLBACK_MENU_CSV = BASE_DIR / "data" / "menu.csv"


def _normalize_column_mapping(columns: list[str]) -> dict[str, str]:
    normalized = {col.lower().strip(): col for col in columns}
    mapping: dict[str, str] = {}

    if 'item' in normalized:
        mapping[normalized['item']] = 'item'
    elif 'name' in normalized:
        mapping[normalized['name']] = 'item'
    elif 'itemname' in normalized:
        mapping[normalized['itemname']] = 'item'

    if 'category' in normalized:
        mapping[normalized['category']] = 'category'
    elif 'cat' in normalized:
        mapping[normalized['cat']] = 'category'

    if 'price' in normalized:
        mapping[normalized['price']] = 'price'
    if 'stock' in normalized:
        mapping[normalized['stock']] = 'stock'
    if 'veg' in normalized:
        mapping[normalized['veg']] = 'veg'
    if 'spicy' in normalized:
        mapping[normalized['spicy']] = 'spicy'
    if 'preparation_time' in normalized:
        mapping[normalized['preparation_time']] = 'preparation_time'
    elif 'prep_time' in normalized:
        mapping[normalized['prep_time']] = 'preparation_time'

    return mapping


def load_menu_csv(csv_path: str | Path | None = None) -> pd.DataFrame:
    """Load the restaurant menu CSV with stock and pricing information."""
    csv_file = Path(csv_path) if csv_path else (DEFAULT_MENU_CSV if DEFAULT_MENU_CSV.exists() else FALLBACK_MENU_CSV)
    menu_df = pd.read_csv(csv_file)
    mapping = _normalize_column_mapping(list(menu_df.columns))

    if 'item' not in mapping.values():
        raise ValueError("Menu CSV must include at least an 'item' column.")

    menu_df = menu_df.rename(columns=mapping)
    menu_df['item'] = menu_df['item'].astype(str).str.strip()

    if 'category' not in menu_df.columns:
        menu_df['category'] = 'Uncategorized'
    menu_df['category'] = menu_df['category'].astype(str).str.strip()

    if 'price' not in menu_df.columns:
        menu_df['price'] = 0.0
    menu_df['price'] = pd.to_numeric(menu_df['price'], errors='coerce').fillna(0.0).astype(float)

    if 'stock' not in menu_df.columns:
        menu_df['stock'] = 50
    menu_df['stock'] = pd.to_numeric(menu_df['stock'], errors='coerce').fillna(0).astype(int)

    if 'veg' not in menu_df.columns:
        menu_df['veg'] = 'no'
    menu_df['veg'] = menu_df['veg'].astype(str).str.strip().str.lower()

    if 'spicy' not in menu_df.columns:
        menu_df['spicy'] = 'no'
    menu_df['spicy'] = menu_df['spicy'].astype(str).str.strip().str.lower()

    if 'preparation_time' not in menu_df.columns:
        menu_df['preparation_time'] = 'unknown'
    menu_df['preparation_time'] = menu_df['preparation_time'].astype(str).str.strip()

    return menu_df
