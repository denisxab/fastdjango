from sqlalchemy import Column, ForeignKey, Integer, String


class User:
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email_user = Column(String, unique=True, index=True)
    snils = Column(String)


class Person:
    __tablename__ = "person"

    id = Column(Integer, primary_key=True, index=True)
    fio = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))
