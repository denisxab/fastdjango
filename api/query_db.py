from sqlalchemy.orm import Session

from .models import User


def get_all_users(db: Session, snils: str = None):
    q = db.query(User)
    if snils:
        q = q.filter(User.snils == snils)
    return q.all()


def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()
