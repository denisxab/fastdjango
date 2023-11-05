"""
Утилиты для асинхронной работы с БД
"""
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from settings import DATABASE_URL_ASYNC, DEBUG

# Инициализация подключения к базе данных
async_engine = create_async_engine(DATABASE_URL_ASYNC, echo=True if DEBUG else False)
# Создание сессии
AsyncSessionLocal = sessionmaker(
    bind=async_engine, class_=AsyncSession, expire_on_commit=False
)


# Функция зависимости для получения сессии базы данных
async def async_get_session() -> AsyncSession:
    """
    from sqlalchemy.ext.asyncio import AsyncSession
    from .models import User
    from sqlalchemy import select


    @router_persons.get("/users/")
    async def read_user_all(session: AsyncSession = Depends(async_get_session)):
        result = await session.execute(select(User))
        return result.scalars().all()
    """
    async with AsyncSessionLocal() as session:
        yield session
