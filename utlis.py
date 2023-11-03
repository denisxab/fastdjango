from database import SessionLocal


# Функция зависимости для получения сессии базы данных
def get_db():
    """
    @router_persons.get("/users/")
    def read_user_all(db: Session = Depends(get_db)):
        users = get_all_users(db)
        return users
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
