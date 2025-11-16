# model.py
import fitz
import os
import easyocr
import re
import cv2
import numpy as np

def pdf_to_png(pdf_path, output_dir="temp_pages", dpi=350):
    """Конвертация PDF в изображения PNG"""
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

reader = easyocr.Reader(['ru'], gpu=False)

def ocr_image(image_path):
    """Распознавание текста с изображения"""
    image_path = preprocess_image(image_path)
    results = reader.readtext(image_path, detail=0, paragraph=True)
    return "\n".join(results)

def preprocess_image(img_path):
    """Предобработка изображения для улучшения качества распознавания"""
    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    
    # Увеличение резкости
    kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
    img = cv2.filter2D(img, -1, kernel)
    
    # Адаптивная бинаризация
    img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                               cv2.THRESH_BINARY, 11, 2)
    
    out = img_path.replace(".png", "_prep.png")
    cv2.imwrite(out, img)
    return out

def clean_text(text: str):
    """Очистка текста от лишних пробелов и символов"""
    text = text.replace("\xa0", " ")
    text = re.sub(r"[ ]{2,}", " ", text)
    return text

def correct_ocr_errors(text):
    """Коррекция распространенных ошибок OCR"""
    corrections = {
        '&': '№',
        '~': '/',
        '`': '',
        "'": '',
        '3а': 'за',
        '0ОО': 'ООО',
        '0О': 'ОО',
        'плс': 'р/с',
        'K/c': 'к/с',
        'Г.': 'г.',
        'Область': 'обл.',
        'город': 'г.',
        'улица': 'ул.',
        'строение': 'стр.',
        'офис': 'оф.',
        'помещ': 'пом.',
        'Ng': '№',
        'Ед:': 'Ед.',
        'Изм': 'изм.',
        'Кол-во': 'Кол-во',
        'руб:': 'руб.',
        'ндС': 'НДС',
        'Ipy6': 'руб.',
        'Bcerоc': 'Всего',
        'аименование': 'Наименование',
        'CUET': 'СЧЕТ',
        'OТ': 'от',
        'Bhиmahиe': 'Внимание',
        'Aheй': 'дней',
        'окупатель': 'Покупатель',
        'Lос': 'ул.',
        'Teл': 'Тел.',
        'Bceгоc': 'Всего',
        'py6': 'руб.',
        'MockObLeba': 'Московцева',
        'dO': 'до',
        'dA': 'да',
        'идату': 'и дату',
        'паi': 'по email',
        'катеринбург': 'Екатеринбург',
        'л': 'ул.',
        'Суходо': 'Суходольская',
        'ьская': 'льская',
        'ерерыв': 'перерыва',
        'риполучении': 'при получении',
        'довере': 'доверенности',
        'ного': 'ного',
        'заKOHа': 'закона',
        'госyдаpсTBенHом': 'государственном',
        'обоpонном': 'оборонном',
        'заказe': 'заказе',
        'Hарушенияокуп': 'нарушения покупателем',
        '1yHKTа': 'пункта',
        'одностороннемпорядке': 'одностороннем порядке',
        'OTKазаTьCяO': 'отказаться от',
        'исполHения': 'исполнения',
        'посTавки': 'поставки',
        'Oплата': 'Оплата',
        'TOrO': 'того',
        'чтO': 'что',
        'lокyпаTелE': 'покупатель',
        'ены': 'обязан',
        'указаны': 'указан',
        'Hа': 'на',
        'отгрузкић': 'отгрузки',
        'циkа': 'цена',
        'Cвepдловская': 'Свердловская',
        'Ekатepинбypг': 'Екатеринбург',
        'yл': 'ул.',
        'Cyxодольсkая': 'Суходольская',
        'KонтактHымлицом': 'Контактным лицом',
        'Cмогоpжeвская': 'Смоторжевская',
        '1ел': 'Тел.',
        'Стоимост': 'Стоимость',
        'доставки': 'доставки',
        'рупногабаритного': 'крупногабаритного',
        'овара': 'товара',
        'ожет': 'может',
        'рассчитанаиндивидуально': 'рассчитана индивидуально',
        'Второй': 'Второй',
        'экземпляр': 'экземпляр',
        'отгрузочногс': 'отгрузочного',
        'Использyется': 'Используется',
        'Kонтyp': 'Контур',
        'Диадок': 'Диадок',
        'овая': 'Новая',
        'услуга': 'услуга',
        'контрактное': 'контрактное',
        'производствс': 'производство',
        'электроники': 'электроники',
        'Ссылканаглавнойстранице': 'Ссылка на главной странице',
        'оборудованиеот': 'оборудование от'
    }
    
    for wrong, correct in corrections.items():
        text = text.replace(wrong, correct)
    
    return text

def extract_document_type(text):
    """Извлечение типа документа с учетом разных форматов"""
    text_lower = text.lower()
    
    if 'счёт-оферта' in text_lower or 'счет-оферта' in text_lower:
        return 'Счёт-оферта'
    elif 'счёт на оплату' in text_lower or 'счет на оплату' in text_lower:
        return 'Счёт на оплату'
    elif 'акт выполненных работ' in text_lower:
        return 'Акт выполненных работ'
    elif 'счёт' in text_lower or 'счет' in text_lower:
        return 'Счёт'
    
    return 'Счёт'

def extract_document_number(text):
    """Извлечение номера документа с коррекцией ошибок OCR"""
    text_corrected = correct_ocr_errors(text)
    
    patterns = [
        r'сч[её]т\s*[№n]\s*([a-za-zа-яё0-9\-/]+)',
        r'[№n]\s*([a-za-zа-яё0-9\-/]+)\s*от',
        r'сч[её]т[^\n]{0,50}?([0-9]+[/\-][0-9]+)',
        r'№\s*(\d+[/\\\-]\d+)',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text_corrected, re.IGNORECASE)
        for match in matches:
            if len(str(match).strip()) > 1:
                return str(match).strip()
    
    return None

def extract_document_date(text):
    """Извлечение даты документа"""
    patterns = [
        r'от\s*(\d{1,2}[.\-/]\d{1,2}[.\-/]\d{2,4})',
        r'(\d{1,2}[.\-/]\d{1,2}[.\-/]\d{4})',
        r'(\d{1,2}\s+[а-я]+\s+\d{4})\s*года?',
    ]
    
    for pattern in patterns:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            return m.group(1)
    
    return None

def extract_inn_kpp(text, entity_type="supplier"):
    """Извлечение ИНН и КПП для поставщика или покупателя"""
    text_corrected = correct_ocr_errors(text)
    
    if entity_type == "supplier":
        # Поиск ИНН поставщика
        supplier_patterns = [
            r'поставщик[^\n]{0,300}?инн\s*([0-9]{10,12})',
            r'инн\s*([0-9]{10,12})[^\n]{0,200}?кпп\s*([0-9]{9})',
        ]
        
        for pattern in supplier_patterns:
            m = re.search(pattern, text_corrected, re.IGNORECASE | re.DOTALL)
            if m:
                inn = m.group(1)
                kpp = m.group(2) if len(m.groups()) > 1 else None
                return inn, kpp
    else:
        # Поиск ИНН покупателя
        buyer_patterns = [
            r'покупатель[^\n]{0,300}?инн\s*([0-9]{10,12})',
            r'инн\s*([0-9]{10,12})[^\n]{0,200}?кпп\s*([0-9]{9})',
        ]
        
        for pattern in buyer_patterns:
            matches = re.findall(pattern, text_corrected, re.IGNORECASE | re.DOTALL)
            if len(matches) > 1:  # Второй найденный ИНН - покупатель
                return matches[1][0], matches[1][1] if len(matches[1]) > 1 else None
    
    # Резервный поиск всех ИНН/КПП
    inn_matches = re.findall(r'инн\s*([0-9]{10,12})', text_corrected, re.IGNORECASE)
    kpp_matches = re.findall(r'кпп\s*([0-9]{9})', text_corrected, re.IGNORECASE)
    
    if entity_type == "supplier" and inn_matches:
        return inn_matches[0], kpp_matches[0] if kpp_matches else None
    elif entity_type == "buyer" and len(inn_matches) > 1:
        return inn_matches[1], kpp_matches[1] if len(kpp_matches) > 1 else None
    
    return None, None

def extract_bank_details(text):
    """Извлечение банковских реквизитов"""
    text_corrected = correct_ocr_errors(text)
    
    # БИК
    bik_match = re.search(r'бик\s*([0-9]{9})', text_corrected, re.IGNORECASE)
    bik = bik_match.group(1) if bik_match else None
    
    # Расчетный счет
    account_match = re.search(r'р/?с\s*([0-9]{20})', text_corrected, re.IGNORECASE)
    account = account_match.group(1) if account_match else None
    
    # Корреспондентский счет
    corr_match = re.search(r'к/?с\s*([0-9]{20})', text_corrected, re.IGNORECASE)
    corr_account = corr_match.group(1) if corr_match else None
    
    # Название банка
    bank_match = re.search(r'в\s+([^\n]{0,100}?банк[^\n]{0,50})', text_corrected, re.IGNORECASE)
    bank_name = bank_match.group(1).strip() if bank_match else None
    
    return bik, account, corr_account, bank_name

def extract_amounts(text):
    """Извлечение денежных сумм"""
    text_corrected = correct_ocr_errors(text)
    
    amounts = {}
    
    # Поиск "Всего с НДС" - основная сумма
    total_patterns = [
        r'всего\s*с\s*ндс[^\d]{0,30}([\d\s.,]+)',
        r'всего\s*к\s*оплате[^\d]{0,30}([\d\s.,]+)',
        r'итого[^\d]{0,30}([\d\s.,]+)\s*$',
    ]
    
    for pattern in total_patterns:
        m = re.search(pattern, text_corrected, re.IGNORECASE)
        if m:
            amounts['total'] = clean_amount(m.group(1))
            break
    
    # Поиск суммы НДС
    vat_patterns = [
        r'ндс\s*[\(]?20%?[\)]?[^\d]{0,30}([\d\s.,]+)',
        r'сумма\s*ндс[^\d]{0,30}([\d\s.,]+)',
    ]
    
    for pattern in vat_patterns:
        m = re.search(pattern, text_corrected, re.IGNORECASE)
        if m:
            amounts['vat'] = clean_amount(m.group(1))
            break
    
    # Поиск суммы без НДС
    without_vat_match = re.search(r'сумма\s*без\s*ндс[^\d]{0,30}([\d\s.,]+)', text_corrected, re.IGNORECASE)
    if without_vat_match:
        amounts['without_vat'] = clean_amount(without_vat_match.group(1))
    
    return amounts

def clean_amount(amount_str):
    """Очистка числовых значений"""
    if not amount_str:
        return None
    
    # Убираем все нецифровые символы, кроме точки и запятой
    cleaned = re.sub(r'[^\d,.]', '', amount_str.strip())
    
    if not cleaned:
        return None
        
    # Заменяем запятую на точку
    cleaned = cleaned.replace(',', '.')
    
    # Убираем лишние точки (оставляем только одну)
    parts = cleaned.split('.')
    if len(parts) > 2:
        cleaned = parts[0] + '.' + ''.join(parts[1:])
    
    return cleaned

def extract_names_and_addresses(text):
    """Извлечение названий и адресов"""
    text_corrected = correct_ocr_errors(text)
    
    supplier_name = None
    buyer_name = None
    supplier_address = None
    buyer_address = None
    
    # Поставщик
    supplier_match = re.search(r'поставщик[^\n]{0,200}?([а-яё\s\"\-\'0-9]{10,100}?)(?=инн|$)', text_corrected, re.IGNORECASE | re.DOTALL)
    if supplier_match:
        supplier_name = supplier_match.group(1).strip()
        # Очистка названия
        supplier_name = re.sub(r'\d', '', supplier_name).strip(' .,:;-')
    
    # Покупатель
    buyer_match = re.search(r'покупатель[^\n]{0,200}?([а-яё\s\"\-\'0-9]{10,100}?)(?=инн|$)', text_corrected, re.IGNORECASE | re.DOTALL)
    if buyer_match:
        buyer_name = buyer_match.group(1).strip()
        buyer_name = re.sub(r'\d', '', buyer_name).strip(' .,:;-')
    
    # Адреса
    address_matches = re.findall(r'\d{6}[^\n]{0,150}', text_corrected)
    if len(address_matches) >= 2:
        supplier_address = address_matches[0].strip()
        buyer_address = address_matches[1].strip()
    elif address_matches:
        supplier_address = address_matches[0].strip()
    
    return supplier_name, buyer_name, supplier_address, buyer_address

def extract_items(text):
    """Извлечение позиций товаров"""
    items = []
    
    # Упрощенный поиск товарных позиций
    lines = text.split('\n')
    for line in lines:
        line_clean = re.sub(r'[^\w\s\d.,-]', '', line).strip()
        
        # Ищем строки с ценами и количествами
        if re.search(r'\d{2,}\s*\d*[,.]?\d*\s*руб', line_clean, re.IGNORECASE):
            # Извлекаем числа
            numbers = re.findall(r'(\d{1,3}(?:\s?\d{3})*[,.]?\d{0,2})', line_clean)
            if len(numbers) >= 2:
                items.append({
                    "name": "Товар/услуга",
                    "qty": "1",
                    "price": clean_amount(numbers[0]),
                    "total": clean_amount(numbers[1])
                })
                break
    
    return items if items else [{"name": "Товары/услуги", "qty": "1", "price": None, "total": None}]

def build_json(text):
    """Формирование итогового JSON"""
    text_corrected = correct_ocr_errors(text)
    
    # Извлечение данных
    doc_type = extract_document_type(text_corrected)
    doc_number = extract_document_number(text_corrected)
    doc_date = extract_document_date(text_corrected)
    
    supplier_inn, supplier_kpp = extract_inn_kpp(text_corrected, "supplier")
    buyer_inn, buyer_kpp = extract_inn_kpp(text_corrected, "buyer")
    
    bik, account, corr_account, bank_name = extract_bank_details(text_corrected)
    amounts = extract_amounts(text_corrected)
    
    supplier_name, buyer_name, supplier_address, buyer_address = extract_names_and_addresses(text_corrected)
    items = extract_items(text_corrected)
    
    return {
        "document_type": doc_type,
        "document_number": doc_number,
        "document_date": doc_date,

        "supplier": {
            "name": supplier_name,
            "inn": supplier_inn,
            "kpp": supplier_kpp,
            "address": supplier_address,
            "bank": bank_name,
            "bik": bik,
            "account": account,
            "correspondent_account": corr_account
        },

        "buyer": {
            "name": buyer_name,
            "inn": buyer_inn,
            "kpp": buyer_kpp,
            "address": buyer_address
        },

        "total_amount": amounts.get('total'),
        "vat_amount": amounts.get('vat'),
        "vat_rate": "20%" if amounts.get('vat') else "Без НДС",
        "amount_words": None,

        "items": items,

        "payment_purpose": None,
        "payment_deadline": None
    }

def process_pdf(pdf_path):
    """Основная функция обработки PDF"""
    pages = pdf_to_png(pdf_path)
    full_text = ""

    print("=" * 80)
    print("РАСПОЗНАВАНИЕ ТЕКСТА ИЗ ДОКУМЕНТА:")
    print("=" * 80)
    
    for i, img in enumerate(pages):
        print(f"\n--- Страница {i+1} ---")
        text = ocr_image(img)
        cleaned_text = clean_text(text)
        full_text += "\n" + cleaned_text
        
        print(cleaned_text)
        print("-" * 40)

    print("\n" + "=" * 80)
    print("ПОЛНЫЙ ТЕКСТ ДОКУМЕНТА:")
    print("=" * 80)
    print(full_text)
    print("=" * 80)

    result = build_json(full_text)
    
    print("\n" + "=" * 80)
    print("ИЗВЛЕЧЕННЫЕ ДАННЫЕ:")
    print("=" * 80)
    print(f"Тип документа: {result['document_type']}")
    print(f"Номер: {result['document_number']}")
    print(f"Дата: {result['document_date']}")
    print(f"ИНН поставщика: {result['supplier']['inn']}")
    print(f"КПП поставщика: {result['supplier']['kpp']}")
    print(f"БИК: {result['supplier']['bik']}")
    print(f"Счет: {result['supplier']['account']}")
    print(f"Итого: {result['total_amount']}")
    print(f"НДС: {result['vat_amount']}")
    print("=" * 80)

    return result

def debug_ocr_only(pdf_path):
    """Функция отладки для вывода только распознанного текста"""
    pages = pdf_to_png(pdf_path)
    full_text = ""

    print("=" * 80)
    print("ОТЛАДКА: ВЕСЬ РАСПОЗНАННЫЙ ТЕКСТ")
    print("=" * 80)
    
    for i, img in enumerate(pages):
        print(f"\n--- Страница {i+1} ---")
        text = ocr_image(img)
        cleaned_text = clean_text(text)
        full_text += "\n" + cleaned_text
        print(cleaned_text)
        print("-" * 40)
    
    print("\n" + "=" * 80)
    print("ОБЪЕДИНЕННЫЙ ТЕКСТ ВСЕХ СТРАНИЦ:")
    print("=" * 80)
    print(full_text)
    
    return full_text