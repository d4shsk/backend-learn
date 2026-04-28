from fastapi import FastAPI
import asyncio

app = FastAPI()

async def read_root():
    await asyncio.sleep(3)  # Имитируем асинхронную операцию, например, запрос к базе данных
    print("Запрос отработан!")

@app.get("/")
async def root():
    asyncio.create_task(read_root())  # Запускаем асинхронную функцию в фоновом режиме
    return {"message": "Запрос получен, обрабатывается!"}
