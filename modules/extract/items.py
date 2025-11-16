# modules/extract/items.py
import pdfplumber

def extract_items_from_pdf(pdf_path: str):
    """
    Универсальный парсер таблиц PDF
    """
    items = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                if not table:
                    continue

                header = table[0]
                rows = table[1:]

                if "№" not in header[0]:
                    continue

                for r in rows:
                    item = {
                        "name": None,
                        "qty": None,
                        "unit": None,
                        "price": None,
                        "total": None
                    }

                    for i, h in enumerate(header):
                        if not h:
                            continue

                        h_low = h.lower()

                        if "наим" in h_low or "товар" in h_low:
                            item["name"] = r[i]
                        elif "кол" in h_low:
                            item["qty"] = r[i]
                        elif "ед" in h_low:
                            item["unit"] = r[i]
                        elif "цен" in h_low:
                            item["price"] = r[i]
                        elif "сум" in h_low:
                            item["total"] = r[i]

                    items.append(item)

    return items
