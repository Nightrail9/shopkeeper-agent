"""
FastAPI 应用生命周期管理
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.clients.embedding_client_manager import embedding_client_manager
from app.clients.es_client_manager import es_client_manager
from app.clients.mysql_client_manager import (
    dw_mysql_client_manager,
    meta_mysql_client_manager,
)
from app.clients.qdrant_client_manager import qdrant_client_manager
from app.core.log import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用启动管理，初始化数据库连接、ES 客户端、Qdrant 客户端等
    """
    qdrant_client_manager.init()
    embedding_client_manager.init()
    es_client_manager.init()
    meta_mysql_client_manager.init()
    dw_mysql_client_manager.init()
    logger.info("Qdrant、Embedding、ES、Meta MySQL、DW MySQL 客户端初始化完成")

    yield

    # 与初始化顺序相反地逐个关闭；单个客户端关闭失败不能中断后续关闭，否则连接资源会悬挂
    for client_manager in (
        dw_mysql_client_manager,
        meta_mysql_client_manager,
        es_client_manager,
        embedding_client_manager,
        qdrant_client_manager,
    ):
        try:
            await client_manager.close()
        except Exception as e:
            logger.error(f"关闭客户端 {type(client_manager).__name__} 失败: {e}")
    logger.info("全部客户端已关闭")
