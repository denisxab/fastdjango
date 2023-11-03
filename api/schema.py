from typing import Optional

from pydantic import BaseModel


class CU_UserSchema(BaseModel):
    username: Optional[str]
    email_user: Optional[str]
    snils: Optional[str]
    level: Optional[int]


class UserSchema(CU_UserSchema):
    id: int


class PersonSchema(BaseModel):
    id: int
    fio: str
    user_id: int
