# modules/extract/entities.py
import re

# универсальная очистка названий организаций
def clean_org_name(name: str | None) -> str | None:
    if not name:
        return name

    name = re.sub(r"\bИНН[\s\d]*$", "", name)
    name = re.sub(r"\bКПП[\s\d]*$", "", name)
    name = re.sub(r"[ ,]+$", "", name)
    name = name.replace(" ,", ",")
    name = re.sub(r"\s{2,}", " ", name)
    return name.strip()


def extract_inn_kpp_block(text: str):
    inn = None
    kpp = None

    m = re.search(r"ИНН[:\s]*([0-9]{10,12})", text, re.IGNORECASE)
    if m:
        inn = m.group(1)

    m = re.search(r"КПП[:\s]*([0-9]{9})", text, re.IGNORECASE)
    if m:
        kpp = m.group(1)

    return inn, kpp


def extract_name_block(text: str, inn: str | None):
    if inn:
        # Берём строку ДО ИНН
        pattern = r"(.{3,100}?)\s*(?:ИНН\s*%s)" % inn
        m = re.search(pattern, text, flags=re.IGNORECASE)
        if m:
            return clean_org_name(m.group(1))

    # fallback — первая строчная строка с ООО/АО/ИП/ПАО
    m = re.search(
        r"(ООО|АО|ПАО|ИП|ЗАО|ОАО)[^\n,]+",
        text,
        re.IGNORECASE
    )
    return m.group(0).strip() if m else None
