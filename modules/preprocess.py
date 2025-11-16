# modules/preprocess.py
import re

def clean_text(text: str) -> str:
    text = text.replace("\xa0", " ")
    text = re.sub(r"[ ]{2,}", " ", text)
    text = re.sub(r"\n{3,}", "\n", text)
    return text.strip()

def normalize(text: str) -> str:
    """
    Универсальная коррекция ошибок PDF/OCR.
    """
    corrections = {
        'Ng': '№',
        'н/н': '№',
        '0ОО': 'ООО',
        'цена,руб': 'цена руб',
        'руб:': 'руб.',
        'Ipy6': 'руб',
        'Oт': 'от',
    }

    for wrong, correct in corrections.items():
        text = text.replace(wrong, correct)

    return text