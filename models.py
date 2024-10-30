import os

from sqlalchemy import JSON, Integer, String, Text
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
POSTGRES_DB = os.getenv('POSTGRES_DB')
POSTGRES_HOST = os.getenv('POSTGRES_HOST', '127.0.0.1')
POSTGRES_PORT = os.getenv('POSTGRES_PORT', '5431')

PG_DSN = (f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@"
         f"{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}")

engine = create_async_engine(PG_DSN)

DbSession = async_sessionmaker(engine, expire_on_commit=False)



class Base(DeclarativeBase, AsyncAttrs):
    pass


class SwapiPeople(Base):
    __tablename__ = "swapi_people"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    birth_year: Mapped[str] = mapped_column(String(100))
    eye_color: Mapped[str] = mapped_column(String(100))
    films: Mapped[str] = mapped_column(Text)  # Список фильмов как строка
    gender: Mapped[str] = mapped_column(String(100))
    hair_color: Mapped[str] = mapped_column(String(100))
    height: Mapped[str] = mapped_column(String(100))
    homeworld: Mapped[str] = mapped_column(String(100))
    mass: Mapped[str] = mapped_column(String(100))
    skin_color: Mapped[str] = mapped_column(String(100))
    species: Mapped[str] = mapped_column(Text)  # Список видов как строка
    starships: Mapped[str] = mapped_column(Text)  # Список кораблей как строка
    vehicles: Mapped[str] = mapped_column(Text)  # Список транспорта как строка
    url: Mapped[str] = mapped_column(String(100))
    created: Mapped[str] = mapped_column(String(100))
    edited: Mapped[str] = mapped_column(String(100))


async def init_orm():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


async def close_orm():
    await engine.dispose()
    
    
        

