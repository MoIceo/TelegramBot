# modules/extract/bank.py
import re

def extract_bank_details(text):
    bik = re.search(r"БИК[: ]*(\d{9})", text)
    rs = re.search(r"(?:р/с|р\.с)[^\d]*(\d{20})", text)
    ks = re.search(r"(?:к/с|кор\.с)[^\d]*(\d{20})", text)

    return {
        "bik": bik.group(1) if bik else None,
        "account": rs.group(1) if rs else None,
        "correspondent_account": ks.group(1) if ks else None
    }
