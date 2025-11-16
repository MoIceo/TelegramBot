# modules/extract/blocks.py
import re

BUYER_MARKERS = [
    "Покупатель", "Заказчик", "Грузополучатель",
    "Клиент", "Плательщик"
]

def split_supplier_buyer(text: str):
    pattern = "(" + "|".join(BUYER_MARKERS) + ")[:\s]"
    parts = re.split(pattern, text, maxsplit=1, flags=re.IGNORECASE)

    if len(parts) < 3:
        return text, ""

    supplier = parts[0]
    buyer = parts[1] + parts[2]
    return supplier, buyer
