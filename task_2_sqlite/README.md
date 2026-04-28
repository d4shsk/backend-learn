## Урок 2
### sqlalchemy
Асинхронное нужно импортировать из `sqlalchemy.ext.asyncio`
### 1. Настройка подключения (Движок и Сессии)

```python
engine = create_async_engine("sqlite+aiosqlite:///./users.db")
new_session = async_sessionmaker(engine, expire_on_commit=False)
```

* **`engine` (Движок):** Это сердце SQLAlchemy. Он отвечает за физическое подключение к базе данных. Строка `"sqlite+aiosqlite:///./users.db"` говорит ему: «Создай/используй базу данных SQLite в файле `users.db` в текущей папке, и используй для этого асинхронный драйвер `aiosqlite`».
* **`async_sessionmaker` (Фабрика сессий):** Сессия — это твоя «рабочая область» или «блокнот» для общения с базой данных. Фабрика `new_session` — это инструмент, который будет штамповать новые сессии каждый раз, когда нам нужно будет что-то прочитать или записать. Свойство `expire_on_commit=False` означает, что после сохранения данных (commit) мы всё ещё сможем читать свойства объектов без повторного запроса к базе.

### 2. Подготовка сессии для FastAPI

```python
async def get_session():
    async with new_session() as session:
        yield session

SessionDep = Annotated[AsyncSession, Depends(get_session)]
```

* FastAPI должен как-то получать доступ к базе данных при каждом запросе пользователя. Функция `get_session` открывает новую сессию (`async with`), передает её в FastAPI (`yield`), а когда запрос завершается — автоматически её закрывает. Это защищает базу от зависаний.

### 3. Описание таблиц (Модели)

```python
class Base(DeclarativeBase):
    pass

class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str]
    age: Mapped[int]
    email: Mapped[str]
```

Это самая важная часть ORM. Мы описываем структуру базы данных на языке Python.
* **`DeclarativeBase`:** Мы создаем базовый класс `Base`. Он работает как реестр: он запоминает все наши таблицы, которые мы унаследуем от него.
* **`UserModel`:** Это наша модель. SQLAlchemy посмотрит на этот класс и поймет, что в базе данных должна быть таблица с именем `users` (благодаря `__tablename__`).
* **`Mapped` и `mapped_column`:** Это современный способ SQLAlchemy сказать, какие колонки будут в таблице. 
    * `Mapped[int]` подсказывает Python (и редактору кода), что здесь будет целое число.
    * `mapped_column(primary_key=True, autoincrement=True)` говорит базе данных: «Это уникальный номер (ID) пользователя, он должен увеличиваться автоматически (1, 2, 3...)».

### 4. Создание базы данных (Инициализация)

```python
@app.post("/init_db", tags=["database"])
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
```

* Здесь мы берем наш «реестр» таблиц (`Base.metadata`) и просим SQLAlchemy выполнить две команды:
    1.  `drop_all`: Удалить все существующие таблицы (осторожно, это удалит все данные!).
    2.  `create_all`: Создать таблицы заново, опираясь на описанный нами класс `UserModel`.
* Поскольку `create_all` — это старая синхронная функция, а мы работаем в асинхронном режиме, мы используем `run_sync`, чтобы обернуть её в асинхронный вызов.

### 5. Чтение данных из базы

```python
@app.get("/users", tags=["users"], response_model=list[UserSchema])
async def read_users(session: SessionDep):
    query = select(UserModel)
    result = await session.execute(query)
    users = result.scalars().all()
    return users
```

* **`select(UserModel)`:** Мы формируем запрос. На языке SQL это звучит как `SELECT * FROM users`.
* **`await session.execute(query)`:** Мы отправляем этот запрос в базу данных через нашу сессию.
* **`result.scalars().all()`:** База данных возвращает ответ в виде сложных «кортежей» (строк таблиц). Метод `.scalars()` вытаскивает из них наши объекты Python (экземпляры `UserModel`), а `.all()` собирает их в обычный список.

Поиск конкретного пользователя выглядит похоже, но с фильтром:
* **`select(UserModel).where(UserModel.id == user_id)`:** Это аналог SQL-запроса `WHERE id = ...`.
* **`result.scalar_one_or_none()`:** Эта команда говорит: «Дай мне один результат. Если ничего не найдено, верни `None`» (вместо того чтобы выдавать ошибку).

### 6. Добавление данных (Запись)

```python
@app.post("/users", tags=["users"])
async def create_user(user: UserAddSchema, session: SessionDep):
    new_user = UserModel(name=user.name, age=user.age, email=user.email)
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    return new_user
```

* Сначала мы создаем обычный объект Python: `new_user = UserModel(...)`. В этот момент в базе данных **ещё ничего нет**.
* **`session.add(new_user)`:** Мы кладем нашего пользователя в сессию (в «черновик»).
* **`session.commit()`:** Мы говорим: «Всё, я закончил, сохраняй изменения в базу по-настоящему!». В этот момент генерируется SQL-запрос `INSERT`, и базе назначается `id` для этого пользователя.
* **`session.refresh(new_user)`:** Мы просим сессию обновить наш объект Python актуальными данными из базы. До этого момента у `new_user` не было ID (он был `None`), а после `refresh` в переменной `new_user.id` появится реальный номер из базы данных.
