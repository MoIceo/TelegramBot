# api.py
import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from model import process_pdf

app = FastAPI()

@app.post("/scan")
async def scan_document(file: UploadFile = File(...)):
    # Проверяем формат
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Можно загружать только PDF-файлы")

    # Сохраняем PDF во временный файл
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as f:
        f.write(await file.read())

    try:
        # Запуск OCR
        data = process_pdf(temp_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

    return JSONResponse(content=data)
