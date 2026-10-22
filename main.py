"""
FastAPI 应用入口
"""

import uuid

import uvicorn
from fastapi import FastAPI, Request
from starlette.responses import Response

from app.api.lifespan import lifespan
from app.api.routers.query_router import query_router
from app.core.context import request_id_ctx_var

app = FastAPI(lifespan=lifespan)

app.include_router(query_router)


@app.middleware("http")
async def add_request_id(request: Request, call_next) -> Response:
    """
    中间件：为每个请求添加唯一 ID 到上下文
    """
    # request_id_ctx_var 声明为 ContextVar[str]，这里要存字符串而不是 UUID 对象
    request_id = str(uuid.uuid4())
    request_id_ctx_var.set(request_id)
    response = await call_next(request)
    return response


def run() -> None:
    """
    控制台入口：启动 ASGI 服务
    """
    # 默认只监听本机回环，问数接口目前没有鉴权，避免直接暴露到局域网
    uvicorn.run(app, host="127.0.0.1", port=8000)
