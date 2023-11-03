from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.query_db import get_all_users, get_user_by_id
from utlis import get_db

router_persons = APIRouter()


@router_persons.get("/persons/")
def some_endpoint():
    return {"message": get_all_users()}


@router_persons.get("/users/")
def read_user_all(db: Session = Depends(get_db)):
    users = get_all_users(db)
    if users is None:
        raise HTTPException(status_code=404, detail="User not found")
    return users


@router_persons.get("/users/{user_id}")
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user
