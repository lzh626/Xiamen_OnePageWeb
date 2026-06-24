import os
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from api.interactions import router as interactions_router
from db.database import init_db
from api.attractions import router as attractions_router
from api.weather import router as weather_router

# 启动时初始化数据库
init_db()

app = FastAPI(title="厦门旅游 Web API")

# 注册路由
app.include_router(attractions_router)
app.include_router(interactions_router)
app.include_router(weather_router)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(_, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"code": exc.status_code, "msg": exc.detail, "data": None},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_, exc):
    return JSONResponse(
        status_code=422,
        content={"code": 422, "msg": "参数校验失败", "data": exc.errors()},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(_, exc):
    return JSONResponse(
        status_code=500,
        content={"code": 500, "msg": f"服务器内部错误: {exc}", "data": None},
    )

# 挂载前端静态文件
frontend_path = os.path.join(os.path.dirname(__file__), 'frontend')

@app.get("/")
def read_root():
    return FileResponse(os.path.join(frontend_path, 'index.html'))

app.mount("/", StaticFiles(directory=frontend_path), name="frontend")
