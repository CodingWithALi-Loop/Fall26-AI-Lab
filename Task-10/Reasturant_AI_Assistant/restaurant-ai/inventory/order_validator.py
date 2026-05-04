import re
from pathlib import Path
from typing import Any, Dict, List
from inventory.stock_manager import StockManager
from inventory.csv_loader import load_menu_csv

QUANTITY_RE = re.compile(r"\b(\d+)\b")
STOPWORDS_RE = re.compile(r"\b(order|please|want|would like|for|to|i|me|my|a|an|the|some|any|kind of|kind)\b", re.I)


def _normalize_query(query: str) -> str:
    value = query.lower().strip()
    value = re.sub(r"[^a-z0-9\s]+", " ", value)
    return re.sub(r"\s+", " ", value)


def _parse_order_segments(query: str) -> List[Dict[str, Any]]:
    normalized = _normalize_query(query)
    segments = re.split(r"\band\b|,|&", normalized)
    parsed = []

    for segment in segments:
        text = segment.strip()
        if not text:
            continue

        quantity_match = QUANTITY_RE.search(text)
        quantity = int(quantity_match.group(1)) if quantity_match else None

        if quantity_match:
            text = (text[:quantity_match.start()] + text[quantity_match.end():]).strip()

        text = STOPWORDS_RE.sub("", text).strip()
        if not text:
            continue

        parsed.append({"quantity": quantity, "item_text": text})

    return parsed


def _join_items(items: List[str]) -> str:
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    return ", ".join(items[:-1]) + " and " + items[-1]


def _strip_trailing_punctuation(value: str) -> str:
    return re.sub(r"[.?!]+$", "", value).strip()


def validate_order_query(query: str, csv_path: str | Path | None = None) -> Dict[str, Any]:
    menu_df = load_menu_csv(csv_path)
    manager = StockManager(menu_df=menu_df)
    parsed = _parse_order_segments(query)

    if not parsed:
        return {
            "success": False,
            "message": "I could not identify any valid menu item in that request. Please specify the dish and quantity clearly.",
            "details": [],
        }

    results: List[Dict[str, Any]] = []
    available_messages: List[str] = []
    issue_messages: List[str] = []

    for entry in parsed:
        requested_quantity = entry["quantity"] or 1
        requested_label = entry["item_text"]
        matched_item = manager.find_item(requested_label)

        if not matched_item:
            issue_messages.append(_strip_trailing_punctuation(
                f"I’m sorry, I could not recognize '{requested_label}' as a menu item."
            ))
            results.append(
                {
                    "requested_text": requested_label,
                    "quantity": requested_quantity,
                    "matched_item": None,
                    "stock": 0,
                    "status": "unknown_item",
                }
            )
            continue

        available_stock = manager.stock_for(matched_item)
        if available_stock == 0:
            issue_messages.append(_strip_trailing_punctuation(
                f"I’m sorry, {matched_item} is currently out of stock."
            ))
            results.append(
                {
                    "requested_text": requested_label,
                    "quantity": requested_quantity,
                    "matched_item": matched_item,
                    "stock": available_stock,
                    "status": "out_of_stock",
                }
            )
            continue

        if requested_quantity > available_stock:
            issue_messages.append(_strip_trailing_punctuation(
                f"We can only fulfill {available_stock} {matched_item} out of your requested {requested_quantity}."
            ))
            results.append(
                {
                    "requested_text": requested_label,
                    "quantity": requested_quantity,
                    "matched_item": matched_item,
                    "stock": available_stock,
                    "status": "insufficient_stock",
                }
            )
            continue

        available_messages.append(_strip_trailing_punctuation(
            f"{requested_quantity} {matched_item} is available, and we currently have {available_stock} in stock."
        ))
        results.append(
            {
                "requested_text": requested_label,
                "quantity": requested_quantity,
                "matched_item": matched_item,
                "stock": available_stock,
                "status": "available",
            }
        )

    if not available_messages and issue_messages:
        final_message = f"{ _join_items(issue_messages) }."
        success = False
    elif available_messages and issue_messages:
        final_message = (
            f"We can confirm { _join_items(available_messages) }. "
            f"However, { _join_items(issue_messages) }."
        )
        success = False
    else:
        final_message = f"Excellent. { _join_items(available_messages) }."
        success = True

    return {
        "success": success,
        "message": final_message,
        "details": results,
    }
