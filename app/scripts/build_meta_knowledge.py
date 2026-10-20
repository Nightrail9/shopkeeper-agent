"""
元数据知识库构建脚本
"""

import argparse
import asyncio
from pathlib import Path

from app.clients.embedding_client_manager import embedding_client_manager
from app.clients.es_client_manager import es_client_manager
from app.clients.mysql_client_manager import (
    dw_mysql_client_manager,
    meta_mysql_client_manager,
)
from app.clients.qdrant_client_manager import qdrant_client_manager
from app.repositories.es.value_es_repository import ValueESRepository
from app.repositories.mysql.dw.dw_mysql_repository import DWMySQLRepository
from app.repositories.mysql.meta.meta_mysql_repository import MetaMySQLRepository
from app.repositories.qdrant.column_qdrant_repository import ColumnQdrantRepository
from app.repositories.qdrant.metric_qdrant_repository import MetricQdrantRepository
from app.services.meta_knowledge_service import MetaKnowledgeService


async def build(config_path: Path):
    """
    初始化依赖并执行元数据知识库构建流程
    """

    # 初始化 Meta MySQL 数据库客户端
    meta_mysql_client_manager.init()

    # 初始化 DW MySQL 数据库客户端
    dw_mysql_client_manager.init()

    # 初始化 Qdrant 数据库客户端
    qdrant_client_manager.init()

    # 初始化 Embedding 客户端
    embedding_client_manager.init()

    # 初始化 Elasticsearch 客户端
    es_client_manager.init()

    try:
        async with (
            meta_mysql_client_manager.session_factory() as meta_session,
            dw_mysql_client_manager.session_factory() as dw_session,
        ):
            # 创建 repositories 对象
            meta_mysql_repository = MetaMySQLRepository(meta_session)
            dw_mysql_repository = DWMySQLRepository(dw_session)
            # 字段和指标分别写入不同的 Qdrant collection，后续可以独立召回
            column_qdrant_repository = ColumnQdrantRepository(qdrant_client_manager.client)
            embedding_client = embedding_client_manager.client
            value_es_repository = ValueESRepository(es_client_manager.client)
            metric_qdrant_repository = MetricQdrantRepository(qdrant_client_manager.client)

            meta_knowledge_service = MetaKnowledgeService(
                meta_mysql_repository=meta_mysql_repository,
                dw_mysql_repository=dw_mysql_repository,
                column_qdrant_repository=column_qdrant_repository,
                embedding_client=embedding_client,
                value_es_repository=value_es_repository,
                metric_qdrant_repository=metric_qdrant_repository,
            )
            await meta_knowledge_service.build(config_path)
    finally:
        await meta_mysql_client_manager.close()
        await dw_mysql_client_manager.close()
        await qdrant_client_manager.close()
        await embedding_client_manager.close()
        await es_client_manager.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="元数据知识库构建脚本")
    parser.add_argument(
        "--config_path",
        type=Path,
        default=Path("conf/meta_config.yaml"),
        help="配置文件路径",
    )
    args = parser.parse_args()
    asyncio.run(build(args.config_path))
