from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.query_db import get_all_users, get_user_by_id
from api.schema import CU_UserSchema, UserSchema
from fhelp.database import get_db

from .models import User

router_persons = APIRouter()


@router_persons.get("/persons/")
def some_endpoint():
    return {"message": get_all_users()}


@router_persons.get("/users/")
def read_user_all(snils: str = None, db: Session = Depends(get_db)):
    users = get_all_users(db, snils)
    if users is None:
        raise HTTPException(status_code=404, detail="User not found")
    return users


@router_persons.get("/users/{user_id}", response_model=UserSchema)
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router_persons.post("/users/", response_model=UserSchema)
def create_user(user_data: CU_UserSchema, db: Session = Depends(get_db)):
    new_user = User(**user_data.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router_persons.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}


@router_persons.put("/users/{user_id}", response_model=UserSchema)
def update_user(user_id: int, user_data: CU_UserSchema, db: Session = Depends(get_db)):
    user = get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    for field, value in user_data.dict().items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user
