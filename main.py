from fastapi import FastAPI
from fastapi_amis_admin.admin import admin
from fastapi_amis_admin.admin.settings import Settings
from fastapi_amis_admin.admin.site import AdminSite

from models import Base, User

# create FastAPI application
app = FastAPI()

# create AdminSite instance
site = AdminSite(
    settings=Settings(
        database_url_async="postgresql+asyncpg://username:password@db/dbname"
    )
)


# register ModelAdmin
@site.register_admin
class UserAdmin(admin.ModelAdmin):
    page_schema = "User"
    # set model
    model = User


# mount AdminSite instance
site.mount_app(app)


# create initial database table
@app.on_event("startup")
async def startup():
    await site.db.async_run_sync(Base.metadata.create_all, is_session=False)


@app.get("/")
def read_root():
    return {"Hello": "World"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
