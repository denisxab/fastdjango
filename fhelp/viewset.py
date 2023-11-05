"""
Автоматизация для построение Views
"""
from copy import deepcopy
from typing import Any, Optional

from fastapi import Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy.orm.decl_api import DeclarativeMeta

from fhelp.database import get_session
from fhelp.database_async import async_get_session
from fhelp.fjwt import get_current_user
from fhelp.utlis import count_rows


async def view_retrieve(session: AsyncSession, model: DeclarativeMeta, pk):
    """Получить запись по PK"""
    name_pk = model.__table__.primary_key.columns.values()[0].name
    result = await session.execute(select(model).filter(getattr(model, name_pk) == pk))
    row = result.scalars().first()
    if row is None:
        raise HTTPException(status_code=404, detail="User not found")
    return row

def sync_view_retrieve(session: Session, model: DeclarativeMeta, pk):
    """Получить запись по PK"""
    name_pk = model.__table__.primary_key.columns.values()[0].name
    return session.query(model).filter(getattr(model, name_pk) == pk).first()


async def view_list(
    session: AsyncSession,
    model: DeclarativeMeta,
    filters: Optional[dict[str, Any]] = None,
    filter_like: Optional[dict[str, Any]] = None,
    limit: int = None,
    offset: int = None,
    order_by: tuple[str] = None,
):
    """Получить список записей, с возможностью фильтрации, limit и offset"""

    query = select(model)

    if filters:
        try:
            filters = {
                k: model.__table__.c[k].type.python_type(v)
                for k, v in filters.items()
                if v
            }
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"{e}")
        query = query.filter_by(**filters)

    if filter_like:
        filter_like = {k: v for k, v in filter_like.items() if v}
        or_clauses = [
            model.__table__.c[k].ilike(v + "%") for k, v in filter_like.items()
        ]
        query = query.filter(or_(*or_clauses))

    if order_by:
        query = query.order_by(*order_by)

    if limit is not None:
        query = query.limit(limit)

    if offset is not None:
        query = query.offset(offset)

    rows = await session.execute(query)
    return rows.scalars().all()


def view_create(session: Session, model: DeclarativeMeta, data: BaseModel):
    """Создать запись"""
    new_row = model(**data.dict())
    session.add(new_row)
    session.commit()
    session.refresh(new_row)
    return new_row


def view_delete(session: Session, model: DeclarativeMeta, pk):
    """Удалить запись по PK"""
    row = sync_view_retrieve(session, model, pk)
    if row is None:
        raise HTTPException(status_code=404, detail="User not found")
    session.delete(row)
    session.commit()
    return {"message": "User deleted successfully"}


def view_update(session: Session, model: DeclarativeMeta, pk, data: BaseModel):
    """Обновить запись по PK"""

    row = sync_view_retrieve(session, model, pk)
    if row is None:
        raise HTTPException(status_code=404, detail="User not found")
    for field, value in data.dict().items():
        setattr(row, field, value)
    session.commit()
    session.refresh(row)
    return row


class FViews:
    def __init__(self):
        super().__init__()

        # R Класс модели
        model = getattr(self, "model")
        if not isinstance(model, DeclarativeMeta):
            raise TypeError("model is not type `DeclarativeMeta`")

        # R Путь по которому подключить
        url = getattr(self, "url")
        if not isinstance(url, str):
            raise TypeError("url is not type `str`")

        # R Схема ответа для GET, POST
        getattr(self, "response_model")
        # R Схема для POST и PUT
        getattr(self, "schema_body")
        # O Доступные фильтры по полям с точным спадением
        self.filter_column_eq = getattr(self, "filter_column_eq", None)
        # O Доступные фильтры по полям с начальным спадением
        self.filter_column_like = getattr(self, "filter_column_like", None)
        # O Нужно ли пагинация для List
        self.page_size = getattr(self, "page_size", None)
        # O Максимальное количество записей на странице
        self.max_page_size = getattr(self, "max_page_size", 1000)
        # O Сортировка для списка
        self.order_by = getattr(self, "order_by", None)

        self.add_api_routes()

    def add_api_routes(self):
        # Динамически указываем тип для Body
        tmp_create_view = lambda data: self.create_view(data)  # noqa E731
        tmp_create_view.__annotations__ = deepcopy(self.create_view.__annotations__)
        tmp_create_view.__annotations__["data"] = self.schema_body
        tmp_update_view = lambda pk, data: self.update_view(pk, data)  # noqa E731
        tmp_update_view.__annotations__ = deepcopy(self.update_view.__annotations__)
        tmp_update_view.__annotations__["data"] = self.schema_body

        if self.page_size and not self.order_by:
            raise ValueError(
                "При использование 'page_size' обязательно используйте 'order_by'"
            )
        if self.page_size and self.page_size > self.max_page_size:
            raise ValueError(
                f"page_size({self.page_size}) > max_page_size({self.max_page_size})",
            )

        # Настройка маршрутизатора
        if self.page_size and self.order_by:
            self.get(f"/{self.url}/")(self.list_view)
        else:
            self.get(f"/{self.url}/", response_model=list[self.response_model])(
                self.list_view
            )
        self.get(f"/{self.url}" + "/{pk}", response_model=self.response_model)(
            self.retrieve_view
        )
        self.post(
            f"/{self.url}/",
            response_model=self.response_model,
        )(tmp_create_view)
        self.delete(f"/{self.url}" + "/{pk}")(self.delete_view)
        self.put(f"/{self.url}" + "/{pk}")(tmp_update_view)

    async def list_view(
        self, request: Request, session: AsyncSession = Depends(async_get_session)
    ):
        """
        Query Params:

        page=Номер страницы
        page_size=Размер страницы
        *filter_column*=Фильтрация по имени поля
        """
        filters = None
        filter_like = None
        query_params = request.query_params._dict
        if self.filter_column_eq:
            filters = {f: query_params.get(f) for f in self.filter_column_eq}
        if self.filter_column_like:
            filter_like = {f: query_params.get(f) for f in self.filter_column_like}
        if self.page_size:
            page = int(query_params.get("page", 0))
            _page_size = int(query_params.get("page_size", self.page_size))

            if _page_size > self.max_page_size:
                raise HTTPException(
                    status_code=400,
                    detail=f"page_size({_page_size}) > max_page_size({self.max_page_size})",
                )

            offset = page * _page_size
            count = await count_rows(session, self.model)
            url_obj = request.url
            url = f"{url_obj.scheme}://{url_obj.netloc}{url_obj.path}"

            next_page = page + 1 if count > (page + 1) * _page_size else None
            previous_page = page - 1 if page - 1 > -1 else None

            return {
                "count": count,
                "next": f"{url}?page={next_page}&page_size={_page_size}"
                if next_page
                else None,
                "previous": f"{url}?page={previous_page}&page_size={_page_size}"
                if previous_page is not None
                else None,
                "results": await view_list(
                    session,
                    self.model,
                    filters,
                    filter_like,
                    limit=_page_size,
                    offset=offset,
                    order_by=self.order_by,
                ),
            }
        return await view_list(
            session, self.model, filters, filter_like, order_by=self.order_by
        )

    async def retrieve_view(
        self, pk: int, session: AsyncSession = Depends(async_get_session)
    ):
        return await view_retrieve(session, self.model, pk)

    def create_view(
        self,
        data: BaseModel,
        session: Session = Depends(get_session),
    ):
        _session = session.dependency().__next__()
        return view_create(_session, self.model, data)

    def delete_view(
        self,
        pk: int,
        session: Session = Depends(get_session),
    ):
        return view_delete(session, self.model, pk)

    def update_view(
        self,
        pk: int,
        data: BaseModel,
        session: Session = Depends(get_session),
    ):
        _session = session.dependency().__next__()
        return view_update(_session, self.model, pk, data)


class FViewsJwt(FViews):
    async def list_view(
        self,
        request: Request,
        session: AsyncSession = Depends(async_get_session),
        current_user: dict = Depends(get_current_user),
    ):
        return await super().list_view(request, session)
        ...

    async def retrieve_view(
        self,
        pk: int,
        session: AsyncSession = Depends(async_get_session),
        current_user: dict = Depends(get_current_user),
    ):
        return await super().retrieve_view(pk, session)

    def create_view(
        self,
        data: BaseModel,
        session: Session = Depends(get_session),
    ):
        return super().create_view(data, session)

    def delete_view(
        self,
        pk: int,
        session: Session = Depends(get_session),
        current_user: dict = Depends(get_current_user),
    ):
        return super().delete_view(pk, session)

    def update_view(
        self,
        pk: int,
        data: BaseModel,
        session: Session = Depends(get_session),
        current_user: dict = Depends(get_current_user),
    ):
        return super().update_view(pk, data, session)
