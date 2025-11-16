# modules/extract/addresses.py
import re

ADDRESS_RE = re.compile(
    r"(?:\b\d{6},\s*)?"                        # индекс
    r"(?:[А-ЯЁа-яё][А-ЯЁа-яё\- ]+?,\s*){1,4}"  # регион/город
    r"(?:ул\.?|улица|проспект|пр-т|пер\.?|переулок|ш\.?|шоссе)\s+[А-ЯЁа-яё0-9\- ]+[, ]*"
    r"(?:д\.?|дом)\s*\d+[А-Яа-я0-9\-]*", 
    re.IGNORECASE
)

def extract_address_block(text: str):
    m = ADDRESS_RE.search(text)
    if m:
        return m.group(0).strip().rstrip(",.")
    return None
