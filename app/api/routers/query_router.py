"""
问数查询接口路由
"""

from typing import Annotated

from fastapi import APIRouter, Depends
from starlette.responses import StreamingResponse

from app.api.dependencies import get_query_service
from app.api.schemas.query_schema import QuerySchema
from app.services.query_service import QueryService

# 当前模块只维护查询相关接口，避免后续所有 API 都挤在 main.py 中
query_router = APIRouter()


@query_router.post("/api/query")
async def query_handler(
    # 请求体参数：FastAPI 会把前端 JSON 自动解析成 QuerySchema
    query: QuerySchema,
    # 服务依赖：FastAPI 会调用 get_query_service，递归组装它所需的仓储和客户端
    query_service: Annotated[QueryService, Depends(get_query_service)],
) -> StreamingResponse:
    """
    接收用户自然语言问题，并流式返回 LangGraph 工作流输出
    """
    return StreamingResponse(
        query_service.query(query.query),
        media_type="text/event-stream",
        # 经过 nginx 等反向代理时默认会缓冲响应，流式输出会被整段攒住
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
