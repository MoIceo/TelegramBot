# modules/pdf_reader.py
import fitz  # PyMuPDF
import pdfplumber

def read_pdf_text(pdf_path: str) -> str:
    """
    Извлечение текста из PDF. Если PDF содержит таблицы — pdfplumber их тоже отдаст.
    """
    text = []

    # 1) pdfplumber
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text.append(page_text)
    except Exception:
        pass

    # 2) PyMuPDF
    if not text:
        doc = fitz.open(pdf_path)
        for page in doc:
            text.append(page.get_text())
        doc.close()

    return "\n".join(text)
