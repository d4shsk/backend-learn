## Урок 1
* fastapi (база)
* pydentic
Наследовать классы с данными от BaseModel
* pytest
Асинхронные тесты помечать
```python
@pytest.mark.asyncio
```
И писать. Видимо нужно, чтобы открылось приложение.
```python
    async with AsyncClient(
        transport=ASGITransport(app=app), 
        base_url="http://test"
    ) as client:
```
`assert условие` - проверяет условие 