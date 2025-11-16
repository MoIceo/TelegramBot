# model.py
from modules.pdf_reader import read_pdf_text
from modules.preprocess import clean_text, normalize
from modules.extract.general import extract_document_type, extract_document_number, extract_document_date
from modules.extract.entities import extract_inn_kpp_block, clean_org_name, extract_name_block
from modules.extract.bank import extract_bank_details
from modules.extract.amounts import extract_amounts
from modules.extract.items import extract_items_from_pdf
from modules.extract.addresses import extract_address_block
from modules.extract.blocks import split_supplier_buyer


def process_pdf(pdf_path: str) -> dict:
    text = read_pdf_text(pdf_path)
    text = normalize(clean_text(text))

    supplier_block, buyer_block = split_supplier_buyer(text)

    # --- Поставщик ---
    supplier_inn, supplier_kpp = extract_inn_kpp_block(supplier_block)
    supplier_name = extract_name_block(supplier_block, supplier_inn)
    supplier_name = clean_org_name(supplier_name)
    supplier_addr = extract_address_block(supplier_block)

    # --- Покупатель ---
    buyer_inn, buyer_kpp = extract_inn_kpp_block(buyer_block)
    buyer_name = extract_name_block(buyer_block, buyer_inn)
    buyer_name = clean_org_name(buyer_name)
    buyer_addr = extract_address_block(buyer_block)

    # --- Банк (ищем только в блоке поставщика) ---
    bank_data = extract_bank_details(supplier_block)

    amounts = extract_amounts(text)
    items = extract_items_from_pdf(pdf_path)

    return {
        "document_type": extract_document_type(text),
        "document_number": extract_document_number(text),
        "document_date": extract_document_date(text),

        "supplier": {
            "name": supplier_name,
            "inn": supplier_inn,
            "kpp": supplier_kpp,
            "address": supplier_addr,
            **bank_data
        },

        "buyer": {
            "name": buyer_name,
            "inn": buyer_inn,
            "kpp": buyer_kpp,
            "address": buyer_addr
        },

        **amounts,
        "items": items,

        "payment_purpose": None,
        "payment_deadline": None
    }