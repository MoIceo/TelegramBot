# model.py
import fitz
import os
import easyocr
import re
import cv2
import numpy as np

def pdf_to_png(pdf_path, output_dir="temp_pages", dpi=350):
    os.makedirs(output_dir, exist_ok=True)

    doc = fitz.open(pdf_path)
    image_paths = []

    for i, page in enumerate(doc):
        mat = fitz.Matrix(dpi/72, dpi/72)
        pix = page.get_pixmap(matrix=mat)
        out_path = os.path.join(output_dir, f"page_{i+1}.png")
        pix.save(out_path)
        image_paths.append(out_path)

    doc.close()
    return image_paths

reader = easyocr.Reader(['ru', 'en'], gpu=False)

def ocr_image(image_path):
    image_path = preprocess_image(image_path)
    results = reader.readtext(image_path, detail=0, paragraph=True)
    return "\n".join(results)

def preprocess_image(img_path):
    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    img = cv2.resize(img, None, fx=1.3, fy=1.3, interpolation=cv2.INTER_LINEAR)
    img = cv2.GaussianBlur(img, (3,3), 0)
    img = cv2.threshold(img, 0, 255, cv2.THRESH_OTSU)[1]
    out = img_path.replace(".png", "_prep.png")
    cv2.imwrite(out, img)
    return out

def clean_text(text: str):
    text = text.replace("\xa0", " ")
    text = re.sub(r"[ ]{2,}", " ", text)
    return text

def extract_document_type(text):
    patterns = [
        r"сч[её]т[\s\-]*оферта",
        r"сч[её]т[\s\-]*договор",
        r"сч[её]т[\s\-]*на[\s\-]*оплату",
        r"акт[\s\-]*выполненных[\s\-]*работ",
        r"сч[её]т"  # общий случай
    ]
    for p in patterns:
        m = re.search(p, text, flags=re.IGNORECASE)
        if m:
            return m.group(0).strip().title()
    return None

def extract_document_number(text):
    m = re.search(
        r"(?:сч[её]т[^\n]{0,20}?№?\s*)([A-Za-zА-Яа-я0-9\-/]+)",
        text,
        flags=re.IGNORECASE
    )
    if m:
        return m.group(1)

    # универсальная попытка
    m = re.search(r"№\s*([A-Za-zА-Яа-я0-9\-/]+)", text)
    return m.group(1) if m else None

def extract_document_date(text):
    # 1. Форматы типа 06.06.2025
    m = re.search(r"(\d{1,2}[.\-/]\d{1,2}[.\-/]\d{2,4})", text)
    if m:
        return m.group(1)

    # 2. Форматы типа "11 сентября 2025 года"
    month_map = {
        "января": "01", "февраля": "02", "марта": "03", "апреля": "04",
        "мая": "05", "июня": "06", "июля": "07", "августа": "08",
        "сентября": "09", "октября": "10", "ноября": "11", "декабря": "12"
    }

    m = re.search(
        r"(\d{1,2})\s+(января|февраля|марта|апреля|мая|июня|июля|августа|"
        r"сентября|октября|ноября|декабря)\s+(\d{4})",
        text,
        flags=re.IGNORECASE
    )

    if m:
        day = m.group(1).zfill(2)
        month = month_map[m.group(2).lower()]
        year = m.group(3)
        return f"{day}.{month}.{year}"

    # 3. Форматы типа "11 сентября 2025 г." или "11 сентября 2025 г"
    m = re.search(
        r"(\d{1,2})\s+(января|февраля|марта|апреля|мая|июня|июля|августа|"
        r"сентября|октября|ноября|декабря)\s+(\d{4})\s*г\.?",
        text,
        flags=re.IGNORECASE
    )

    if m:
        day = m.group(1).zfill(2)
        month = month_map[m.group(2).lower()]
        year = m.group(3)
        return f"{day}.{month}.{year}"

    return None

def extract_inn(text):
    m = re.search(r"ИНН\s*/\s*КПП\s*([0-9]{10,12})", text, flags=re.IGNORECASE)
    if m: return m.group(1)

    m = re.search(r"ИНН[: ]*([0-9]{10,12})", text, flags=re.IGNORECASE)
    return m.group(1) if m else None


def extract_kpp(text):
    m = re.search(r"ИНН\s*/\s*КПП\s*[0-9]{10,12}\s*/\s*([0-9]{9})", text, re.IGNORECASE)
    if m: return m.group(1)

    m = re.search(r"КПП[: ]*([0-9]{9})", text, re.IGNORECASE)
    return m.group(1) if m else None


def extract_bik(text):
    m = re.search(r"БИК[: ]*([0-9]{9})", text, re.IGNORECASE)
    return m.group(1) if m else None

def extract_account(text):
    m = re.search(r"(?:р[\/ ]?с|расчетный счет)[^\d]*([0-9]{20})", text, re.IGNORECASE)
    return m.group(1) if m else None

def extract_corr_account(text):
    m = re.search(r"(?:кор[\/ ]?сч|к\/с)[^\d]*([0-9]{20})", text, re.IGNORECASE)
    return m.group(1) if m else None

def extract_total_amount(text):
    m = re.search(
        r"(?:итого|к оплате)[^0-9]*([\d\s.,]+ ?(?:руб|₽)?)",
        text,
        re.IGNORECASE
    )
    return m.group(1).strip() if m else None

def extract_vat_amount(text):
    m = re.search(
        r"(?:НДС|в т\.ч\. НДС)[^0-9]*([\d\s.,]+ ?(?:руб|₽)?)",
        text,
        re.IGNORECASE
    )
    return m.group(1).strip() if m else None

def extract_vat_rate(text):
    m = re.search(r"НДС\s*\(?\s*(\d{1,2}%|без НДС)\s*\)?", text, re.IGNORECASE)
    return m.group(1) if m else None


def extract_items(text):
    items = []
    lines = text.split("\n")

    for line in lines:
        if re.search(r"\d+[,\.]?\d*\s*(руб|₽)", line, re.IGNORECASE):
            items.append({"raw": line.strip()})

    return items


def build_json(text):
    return {
        "document_type": extract_document_type(text),
        "document_number": extract_document_number(text),
        "document_date": extract_document_date(text),

        "supplier": {
            "name": None,
            "inn": extract_inn(text),
            "kpp": extract_kpp(text),
            "address": None,
            "bank": None,
            "bik": extract_bik(text),
            "account": extract_account(text),
            "correspondent_account": extract_corr_account(text)
        },

        "buyer": {
            "name": None,
            "inn": None,
            "kpp": None,
            "address": None
        },

        "total_amount": extract_total_amount(text),
        "vat_amount": extract_vat_amount(text),
        "vat_rate": extract_vat_rate(text),
        "amount_words": None,

        "items": extract_items(text),

        "payment_purpose": None,
        "payment_deadline": None
    }

def process_pdf(pdf_path):
    pages = pdf_to_png(pdf_path)
    full_text = ""

    for img in pages:
        text = ocr_image(img)
        full_text += "\n" + clean_text(text)

    return build_json(full_text)