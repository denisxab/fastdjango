from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.schema import CU_PersonSchema, CU_UserSchema, PersonSchema, UserSchema
from fhelp.database_async import async_get_session
from fhelp.fjwt import get_current_user
from fhelp.viewset import FViews, FViewsJwt, view_retrieve

from .models import Person, User

router_persons = APIRouter()


class UsersRouter(FViewsJwt, APIRouter):
    model = User
    url = "users"
    response_model = UserSchema
    schema_body = CU_UserSchema
    filter_column_eq = ("level",)
    filter_column_like = ("snils",)
    page_size = 2
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
    #     self, snils: str = None, db: Session = Depends(session)
    # ) -> list[UserSchema]:
    #     return view_list(db, User, filters={"snils": snils})

    # def retrieve_user(self, user_id: int, db: Session = Depends(session)) -> UserSchema:
    #     return view_retrieve(db, User, user_id)

    # def create_user(
    #     self, user_data: CU_UserSchema, db: Session = Depends(session)
    # ) -> UserSchema:
    #     return view_create(db, User, user_data)

    # def delete_user(self, user_id: int, db: Session = Depends(session)):
    #     return view_delete(db, User, user_id)

    # def update_user(
    #     self, user_id: int, user_data: CU_UserSchema, db: Session = Depends(session)
    # ):
    #     return view_update(db, User, user_id, user_data)


class PersonRouter(FViews, APIRouter):
    model = Person
    url = "person"
    response_model = PersonSchema
    schema_body = CU_PersonSchema
    filter_column_eq = ("fio", "user_id")
    order_by = ("id",)

    async def list_view(
        self,
        request: Request,
        session: AsyncSession = Depends(async_get_session),
        current_user: dict = Depends(get_current_user),
    ):
        rows = await super().list_view(request, session)
        result = []

        for row in rows:
            user = await view_retrieve(session, User, row.user_id)
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


async def async_view_list(session, model):
    """Получить запись по PK"""
    result = await session.execute(select(model))
    return result.scalars().all()


@router_persons.get("/async_endpoint/")
async def async_endpoint(session: AsyncSession = Depends(async_get_session)):
    user = await async_view_list(session, User)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


router_persons.include_router(UsersRouter())
router_persons.include_router(PersonRouter())
