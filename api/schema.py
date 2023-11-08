from typing import Optional

from pydantic import BaseModel


class CU_UserSchema(BaseModel):
    username: Optional[str]
    email_user: Optional[str]
    snils: Optional[str]
    level: Optional[int]

    class Config:
        orm_mode = True


class UserSchema(CU_UserSchema):
    id: int

    class Config:
        orm_mode = True


class PersonSchema(BaseModel):
    id: int
    fio: str
    user_id: UserSchema

    class Config:
        orm_mode = True


class CU_PersonSchema(BaseModel):
    fio: str
    user_id: int

    class Config:
        orm_mode = True
