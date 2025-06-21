from fastapi import FastAPI, File, UploadFile, HTTPException
import requests
import base64

app = FastAPI()

IMGUR_CLIENT_ID = "08f9df183a20c6d"
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
ALLOWED_EXTENSIONS = {
    "jpg", "jpeg", "png", "gif", "tiff", "bmp", "pdf",
    "x-icon", "webp", "heif", "heic"
}


@app.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    # Проверка расширения
    ext = file.filename.split(".")[-1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Неподдерживаемый формат файла.")

    # Чтение и проверка размера
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="Файл слишком большой. Максимум 10 МБ.")

    # Кодирование и отправка в Imgur
    encoded = base64.b64encode(content).decode()

    headers = {
        "Authorization": f"Client-ID {IMGUR_CLIENT_ID}"
    }

    data = {
        "image": encoded,
        "type": "base64"
    }

    response = requests.post("https://api.imgur.com/3/image", headers=headers, data=data)
    result = response.json()

    if response.status_code == 200 and result.get("success"):
        return {"link": result["data"]["link"]}
    else:
        raise HTTPException(status_code=500, detail="Ошибка при загрузке в Imgur.")
