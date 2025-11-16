# bot.py
import logging
import requests
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, Message
from aiogram.enums import ParseMode

from bot_token import TOKEN # файл с переменной TOKEN = "ВАШ_ТОКЕН"

API_URL = "http://localhost:8000/scan"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Хранение состояния
waiting_for_pdf = {}


# ---------- Кнопки ----------
def main_keyboard():
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Информация"), KeyboardButton(text="Скан")]],
        resize_keyboard=True
    )
    return kb


# ---------- Хелпер форматирования ----------
def escape_markdown(text):
    """Экранирование специальных символов для MarkdownV2"""
    if text is None:
        return ""
    
    escape_chars = r'_*[]()~`>#+-=|{}!'
    return str(text).translate(str.maketrans({c: f'\\{c}' for c in escape_chars}))

def fmt(label, value):
    """
    Показывает строку только если значение существует.
    """
    if value is None or value == "" or value == "None":
        return ""
    
    escaped_value = escape_markdown(value)
    return f"**{label}:** {escaped_value}\n"


# ---------- Команда /start ----------
@dp.message(Command("start"))
async def start_cmd(message: Message):
    await message.answer(
        "Привет! 👋\nЭтот бот распознаёт важные поля из PDF-счётов.",
        reply_markup=main_keyboard()
    )


# ---------- Информация ----------
@dp.message(F.text == "Информация")
async def info_cmd(message: Message):
    await message.answer(
        "ℹ️ *Как пользоваться ботом*\n\n"
        "1) Нажмите кнопку *Скан*\n"
        "2) Отправьте PDF-файл\n"
        "3) Бот обработает документ и пришлёт ключевые поля:\n"
        "- Тип документа\n"
        "- Номер\n"
        "- Дата\n"
        "- Поставщик и покупатель\n"
        "- Суммы\n"
        "- Табличная часть",
        parse_mode=ParseMode.MARKDOWN
    )


# ---------- Сканирование ----------
@dp.message(F.text == "Скан")
async def scan_cmd(message: Message):
    waiting_for_pdf[message.from_user.id] = True
    await message.answer("📄 Пришлите PDF-файл для сканирования.")


# ---------- Обработка PDF ----------
@dp.message(F.document)
async def handle_document(message: Message):
    user_id = message.from_user.id

    if not waiting_for_pdf.get(user_id):
        await message.answer("Нажмите 'Скан', чтобы начать обработку 📄", reply_markup=main_keyboard())
        return

    doc = message.document

    # Проверяем формат
    if not doc.file_name.lower().endswith(".pdf"):
        await message.answer("❌ Можно загружать только PDF-файлы.")
        waiting_for_pdf[user_id] = False
        return

    # Загружаем файл
    file_info = await bot.get_file(doc.file_id)
    file_bytes = await bot.download_file(file_info.file_path)

    # Отправляем в API
    files = {"file": (doc.file_name, file_bytes, "application/pdf")}

    try:
        response = requests.post(API_URL, files=files)
    except Exception as e:
        logging.error(f"API error: {e}")
        await message.answer("⚠️ Ошибка соединения с API.")
        waiting_for_pdf[user_id] = False
        return

    if response.status_code != 200:
        await message.answer(f"⚠️ API вернуло ошибку: {response.text}")
        waiting_for_pdf[user_id] = False
        return

    data = response.json()

    # ---------- Формирование ответа ----------
    supplier = data.get("supplier", {})
    buyer = data.get("buyer", {})

    text = "📑 *Результаты сканирования:*\n\n"

    # --- Документ ---
    text += fmt("Тип документа", data.get("document_type"))
    text += fmt("Номер", data.get("document_number"))
    text += fmt("Дата", data.get("document_date"))
    text += "\n"

    # --- Поставщик ---
    if any(v for v in supplier.values() if v):
        text += "👨‍💼 *Поставщик:*\n"
        text += fmt("Название", supplier.get("name"))
        text += fmt("ИНН", supplier.get("inn"))
        text += fmt("КПП", supplier.get("kpp"))
        text += fmt("Адрес", supplier.get("address"))
        text += fmt("Банк", supplier.get("bank"))
        text += fmt("БИК", supplier.get("bik"))
        text += fmt("Расчётный счёт", supplier.get("account"))
        text += fmt("Корр. счёт", supplier.get("correspondent_account"))
        text += "\n"

    # --- Покупатель ---
    if any(v for v in buyer.values() if v):
        text += "🧾 *Покупатель:*\n"
        text += fmt("Название", buyer.get("name"))
        text += fmt("ИНН", buyer.get("inn"))
        text += fmt("КПП", buyer.get("kpp"))
        text += fmt("Адрес", buyer.get("address"))
        text += "\n"

    # --- Суммы ---
    text += "💰 *Суммы:*\n"
    text += fmt("Итого", data.get("total_amount"))
    text += fmt("Сумма НДС", data.get("vat_amount"))
    text += fmt("Ставка НДС", data.get("vat_rate"))
    text += "\n"

    # --- Позиции ---
    items = data.get("items", [])
    if items:
        text += "📦 *Позиции:*\n"
        for item in items:
            line = ""
            if item.get("name"):
                line += f"• {escape_markdown(item['name'])}"
            if item.get("qty"):
                line += f" — {escape_markdown(item['qty'])} шт"
            if item.get("price"):
                line += f", цена {escape_markdown(item['price'])}"
            if item.get("total"):
                line += f", сумма {escape_markdown(item['total'])}"
            text += line + "\n"
        text += "\n"

    waiting_for_pdf[user_id] = False

    if len(text) > 4096:
        text = text[:4090] + "\n..."

    await message.answer(text, parse_mode=ParseMode.MARKDOWN, reply_markup=main_keyboard())


# ---------- Если текст неизвестен ----------
@dp.message()
async def other(message: Message):
    await message.answer(
        "Используйте меню 👆",
        reply_markup=main_keyboard()
    )


# ---------- Запуск ----------
async def main():
    print("Бот запущен!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())