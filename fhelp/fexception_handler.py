import fastapi
from fastapi import HTTPException
from fastapi.responses import JSONResponse


async def f_404_handler(request, exc: HTTPException, app: fastapi):
    """Обработка 404 HTTP исключения"""
    available_urls = list(set(route.path for route in app.routes))
    available_urls.sort()

    start_url_path = "/".join(request.url.path.split("/")[:-1])
    result_list_url = [x for x in available_urls if x.startswith(start_url_path)]
    if not result_list_url:
        result_list_url = available_urls

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "available_urls": result_list_url,
        },
    )
