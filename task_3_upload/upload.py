from fastapi import FastAPI, File, UploadFile
import asyncio

from fastapi.responses import FileResponse

app = FastAPI()

@app.post("/files/upload")
async def upload(uploaded_file: UploadFile):
    file = uploaded_file.file
    filename = uploaded_file.filename
    with open(f"uploaded_{filename}", "wb") as buffer:
        buffer.write(file.read())
    return {"message": "Файл получен, обрабатывается!"}

@app.post("/files/multiple_upload")
async def multiple_upload(uploaded_files: list[UploadFile]):
    for uploaded_file in uploaded_files:
        file = uploaded_file.file
        filename = uploaded_file.filename
        with open(f"uploaded_{filename}", "wb") as buffer:
            buffer.write(file.read())
    return {"message": "Файлы получены, обрабатываются!"}

@app.get("/files/{filename}")
async def get_file(filename: str):
    return FileResponse(f"uploaded_{filename}")