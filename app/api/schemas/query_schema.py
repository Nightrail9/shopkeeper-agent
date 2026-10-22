"""
问数接口请求体定义
"""

from pydantic import BaseModel, Field


class QuerySchema(BaseModel):
    # 空问题和超长问题都会白跑一遍问数链路，在这里直接挡掉
    query: str = Field(min_length=1, max_length=500, description="用户的自然语言问数问题")
