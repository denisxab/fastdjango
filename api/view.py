from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from api.schema import CU_PersonSchema, CU_UserSchema, PersonSchema, UserSchema
from fhelp.database import get_db
from fhelp.viewset import FBaseRouter, view_retrieve

from .models import Person, User

router_persons = APIRouter()


class UsersRouter(FBaseRouter, APIRouter):
    model = User
    url = "users"
    response_model = UserSchema
    schema_body = CU_UserSchema
    filter_column = ("snils", "level")
    size_page = 2
    order_by = ("id",)

    # def __init__(self):
    #     super().__init__()
    #     self.add_api_routes()

    # def add_api_routes(self):
    #     self.get("/users/")(self.list_user)
    #     self.get("/users/{user_id}")(self.retrieve_user)
    #     self.post("/users/")(self.create_user)
    #     self.delete("/users/{user_id}")(self.delete_user)
    #     self.put("/users/{user_id}")(self.update_user)

    # def list_user(
    #     self, snils: str = None, db: Session = Depends(get_db)
    # ) -> list[UserSchema]:
    #     return view_list(db, User, filters={"snils": snils})

    # def retrieve_user(self, user_id: int, db: Session = Depends(get_db)) -> UserSchema:
    #     return view_retrieve(db, User, user_id)

    # def create_user(
    #     self, user_data: CU_UserSchema, db: Session = Depends(get_db)
    # ) -> UserSchema:
    #     return view_create(db, User, user_data)

    # def delete_user(self, user_id: int, db: Session = Depends(get_db)):
    #     return view_delete(db, User, user_id)

    # def update_user(
    #     self, user_id: int, user_data: CU_UserSchema, db: Session = Depends(get_db)
    # ):
    #     return view_update(db, User, user_id, user_data)


class PersonRouter(FBaseRouter, APIRouter):
    model = Person
    url = "person"
    response_model = PersonSchema
    schema_body = CU_PersonSchema
    filter_column = ("fio", "user_id")
    order_by = ("id",)

    def list_view(self, request: Request, db: Session = Depends(get_db)):
        rows = super().list_view(request, db)
        result = []

        for row in rows:
            user = view_retrieve(db, User, row.user_id)
            result.append(
                {
                    "id": row.id,
                    "fio": row.fio,
                    "user_id": {
                        "id": row.user_id,
                        "username": user.username,
                        "email_user": user.email_user,
                        "snils": user.snils,
                        "level": user.level,
                    },
                }
            )
        return result


router_persons.include_router(UsersRouter())
router_persons.include_router(PersonRouter())
