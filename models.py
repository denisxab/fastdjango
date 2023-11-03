from sqlalchemy.ext.declarative import declarative_base

from api.models import Person, User

Base = declarative_base()


class UserQ(Base, User):
    ...


class PersonQ(Base, Person):
    ...
