# modules/extract/amounts.py
import re

def clean_amount(v):
    if not v:
        return None
    v = re.sub(r"[^\d.,]", "", v)
    return v.replace(",", ".").strip()

def extract_amounts(text):
    total = re.search(r"(?:Итого|Всего)[^\d]+([\d\s.,]+)", text)
    vat = re.search(r"НДС[^\d]+([\d\s.,]+)", text)

    return {
        "total_amount": clean_amount(total.group(1)) if total else None,
        "vat_amount": clean_amount(vat.group(1)) if vat else None,
        "vat_rate": "20%" if vat else "Без НДС"
    }
