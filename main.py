from fastapi import FastAPI

from api.view import router_persons

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


# Добавляем роутер к приложению
app.include_router(router_persons)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
