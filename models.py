from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email_user = Column(String, unique=True, index=True)
    snils = Column(String)


class Person(Base):
    __tablename__ = "core.person"

    id = Column(Integer, primary_key=True, index=True)
    fio = Column(String)
    user_id = Column(
        Integer, ForeignKey("users.id")
    )  # Добавляем столбец user_id как внешний ключ
