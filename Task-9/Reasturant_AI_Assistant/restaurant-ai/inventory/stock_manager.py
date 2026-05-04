import re
from pathlib import Path
from typing import Optional
import pandas as pd
from inventory.csv_loader import load_menu_csv, DEFAULT_MENU_CSV, FALLBACK_MENU_CSV


class StockManager:
    def __init__(self, menu_df: pd.DataFrame | None = None, csv_path: str | Path | None = None):
        self.csv_path = Path(csv_path) if csv_path else (DEFAULT_MENU_CSV if DEFAULT_MENU_CSV.exists() else FALLBACK_MENU_CSV)
        self.menu_df = menu_df if menu_df is not None else load_menu_csv(self.csv_path)
        self.menu_df["item_normalized"] = self.menu_df["item"].str.lower().str.strip()
        self.menu_df = self.menu_df.drop_duplicates(subset=["item_normalized"], keep="first")
        self.index = {row["item_normalized"]: row["item"] for _, row in self.menu_df.iterrows()}

    @staticmethod
    def _normalize_name(value: str) -> str:
        normalized = re.sub(r"[^a-z0-9 ]+", " ", value.lower()).strip()
        return re.sub(r"\s+", " ", normalized)

    @staticmethod
    def _singularize(value: str) -> str:
        value = value.strip().lower()
        if value.endswith("ies"):
            return value[:-3] + "y"
        if value.endswith("s") and len(value) > 3:
            return value[:-1]
        return value

    def _normalize_item(self, value: str) -> str:
        return self._singularize(self._normalize_name(value))

    def find_item(self, item_name: str) -> Optional[str]:
        item_name_norm = self._normalize_item(item_name)
        if not item_name_norm:
            return None

        for menu_item_norm, menu_item in self.index.items():
            if self._normalize_item(menu_item_norm) == item_name_norm:
                return menu_item

        for menu_item_norm, menu_item in self.index.items():
            if item_name_norm in self._normalize_item(menu_item_norm):
                return menu_item

        for menu_item_norm, menu_item in self.index.items():
            if self._normalize_item(menu_item_norm) in item_name_norm:
                return menu_item

        return None

    def stock_for(self, item_name: str) -> int:
        matched = self.find_item(item_name)
        if not matched:
            return 0
        return int(self.menu_df.loc[self.menu_df["item"] == matched, "stock"].iloc[0])

    def item_exists(self, item_name: str) -> bool:
        return self.find_item(item_name) is not None

    def update_stock(self, item_name: str, quantity: int) -> bool:
        """Update stock by reducing quantity. Returns True if successful."""
        matched = self.find_item(item_name)
        if not matched:
            return False

        current_stock = self.stock_for(matched)
        if current_stock < quantity:
            return False

        # Update in DataFrame
        self.menu_df.loc[self.menu_df["item"] == matched, "stock"] = current_stock - quantity

        # Save to CSV
        try:
            self.menu_df.drop(columns=["item_normalized"], errors="ignore").to_csv(self.csv_path, index=False)
            return True
        except Exception as e:
            print(f"Error saving stock update: {e}")
            return False

    def get_item_details(self, item_name: str) -> Optional[Dict]:
        """Get full item details including price, category, and preparation time."""
        matched = self.find_item(item_name)
        if not matched:
            return None

        row = self.menu_df[self.menu_df["item"] == matched].iloc[0]
        return {
            "item": row["item"],
            "category": row.get("category", "Uncategorized"),
            "price": float(row.get("price", 0.0) or 0.0),
            "stock": int(row.get("stock", 0) or 0),
            "veg": str(row.get("veg", "no")).strip().lower() == "yes",
            "spicy": str(row.get("spicy", "no")).strip().lower() == "yes",
            "preparation_time": str(row.get("preparation_time", "unknown")).strip()
        }
