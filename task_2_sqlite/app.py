from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Annotated
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import select

app = FastAPI()


engine = create_async_engine("sqlite+aiosqlite:///./users.db")
new_session = async_sessionmaker(engine, expire_on_commit=False)

async def get_session():
    async with new_session() as session:
        yield session

SessionDep = Annotated[AsyncSession, Depends(get_session)]

class Base(DeclarativeBase):
    pass

class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str]
    age: Mapped[int]
    email: Mapped[str]


class UserAddSchema(BaseModel):
    name: str
    age: int = Field(ge=0, description="Возраст должен быть неотрицательным")
    email: EmailStr

class UserSchema(UserAddSchema):
    id: int

@app.post("/init_db", tags=["database"])
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    return {"message": "Database initialized"}

@app.get("/users", tags=["users"], response_model=list[UserSchema])
async def read_users(session: SessionDep):
    query = select(UserModel)
    result = await session.execute(query)
    users = result.scalars().all()
    return users

@app.get("/users/{user_id}", tags=["users"], response_model=UserSchema)
async def get_user(user_id: int, session: SessionDep):
    query = select(UserModel).where(UserModel.id == user_id)
    result = await session.execute(query)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.post("/users", tags=["users"])
async def create_user(user: UserAddSchema, session: SessionDep):
    new_user = UserModel(name=user.name, age=user.age, email=user.email)
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    return new_user
    