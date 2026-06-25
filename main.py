import logging
import os
import time
import uuid

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from api.interactions import router as interactions_router
from db.database import init_db
from api.attractions import router as attractions_router
from api.weather import router as weather_router
from api.recommend import router as recommend_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("xiamen-travel")

init_db()

app = FastAPI(title="厦门旅游 Web API")


@app.middleware("http")
async def add_request_id_and_log(request: Request, call_next):
    request_id = str(uuid.uuid4())[:8]
    request.state.request_id = request_id

    start = time.perf_counter()
    response = await call_next(request)
    elapsed_ms = (time.perf_counter() - start) * 1000

    logger.info(
        "request_id=%s | %s %s | %d | %.1fms",
        request_id,
        request.method,
        request.url.path,
        response.status_code,
        elapsed_ms,
    )

    response.headers["X-Request-ID"] = request_id
    return response


app.include_router(attractions_router)
app.include_router(interactions_router)
app.include_router(weather_router)
app.include_router(recommend_router)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc):
    request_id = getattr(request.state, "request_id", "-")
    logger.warning("request_id=%s | HTTP %d | %s", request_id, exc.status_code, exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content={"code": exc.status_code, "msg": exc.detail, "data": None},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc):
    request_id = getattr(request.state, "request_id", "-")
    logger.warning("request_id=%s | 422 ValidationError", request_id)
    return JSONResponse(
        status_code=422,
        content={"code": 422, "msg": "参数校验失败", "data": exc.errors()},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc):
    request_id = getattr(request.state, "request_id", "-")
    logger.error("request_id=%s | 500 InternalError | %s", request_id, exc)
    return JSONResponse(
        status_code=500,
        content={"code": 500, "msg": f"服务器内部错误: {exc}", "data": None},
    )


frontend_path = os.path.join(os.path.dirname(__file__), "frontend")


@app.get("/")
def read_root():
    return FileResponse(os.path.join(frontend_path, "index.html"))


app.mount("/", StaticFiles(directory=frontend_path), name="frontend")
