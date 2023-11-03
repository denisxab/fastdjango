from pydantic import BaseModel


class UserSchema(BaseModel):
    id: int
    username: str
    email_user: str
    snils: str


class PersonSchema(BaseModel):
    id: int
    fio: str
    user_id: int


class CU_UserSchema(BaseModel):
    username: str
    email_user: str
    snils: str
