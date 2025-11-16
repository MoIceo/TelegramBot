# modules/extract/general.py
import re
from modules.preprocess import normalize

def extract_document_type(text):
    t = text.lower()
    if "счет на оплату" in t or "счёт на оплату" in t:
        return "Счёт на оплату"
    if "счет-оферта" in t:
        return "Счёт-оферта"
    if "акт выполненных работ" in t:
        return "Акт выполненных работ"
    if "счет" in t or "счёт" in t:
        return "Счёт"
    return None

def extract_document_number(text):
    text = normalize(text)
    patterns = [
        r"сч[её]т\s*№\s*([A-Za-zА-Яа-я0-9\-\/]+)",
        r"№\s*([A-Za-zА-Яа-я0-9\-\/]+)\s*от",
    ]
    for p in patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            return m.group(1)
    return None

def extract_document_date(text):
    m = re.search(r"(\d{1,2}[.\-/]\d{1,2}[.\-/]\d{4})", text)
    if m:
        return m.group(1)
    return None
