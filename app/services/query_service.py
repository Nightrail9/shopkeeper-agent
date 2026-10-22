"""
问数查询服务
"""

import json
from collections.abc import AsyncGenerator

from langchain_core.embeddings import Embeddings

from app.agent.context import DataAgentContext
from app.agent.graph import graph
from app.agent.state import DataAgentState
from app.repositories.es.value_es_repository import ValueESRepository
from app.repositories.mysql.dw.dw_mysql_repository import DWMySQLRepository
from app.repositories.mysql.meta.meta_mysql_repository import MetaMySQLRepository
from app.repositories.qdrant.column_qdrant_repository import ColumnQdrantRepository
from app.repositories.qdrant.metric_qdrant_repository import MetricQdrantRepository


class QueryService:
    """
    封装一次问数查询所需的业务编排逻辑
    """

    def __init__(
        self,
        meta_mysql_repository: MetaMySQLRepository,
        embedding_client: Embeddings,
        dw_mysql_repository: DWMySQLRepository,
        column_qdrant_repository: ColumnQdrantRepository,
        metric_qdrant_repository: MetricQdrantRepository,
        value_es_repository: ValueESRepository,
    ):
        self.meta_mysql_repository = meta_mysql_repository
        self.dw_mysql_repository = dw_mysql_repository

        self.embedding_client = embedding_client
        self.column_qdrant_repository = column_qdrant_repository
        self.metric_qdrant_repository = metric_qdrant_repository
        self.value_es_repository = value_es_repository

    async def query(self, query: str) -> AsyncGenerator[str, None]:
        """
        执行一次问数查询
        """
        state = DataAgentState(query=query)
        context = DataAgentContext(
            column_qdrant_repository=self.column_qdrant_repository,
            embedding_client=self.embedding_client,
            metric_qdrant_repository=self.metric_qdrant_repository,
            value_es_repository=self.value_es_repository,
            meta_mysql_repository=self.meta_mysql_repository,
            dw_mysql_repository=self.dw_mysql_repository,
        )

        # SSE 的 data 字段必须是单行，json.dumps 默认不换行；加 indent 会让后续行被
        # 解析成未知字段而丢弃，前端只能拿到被截断的 "{"
        try:
            async for chunk in graph.astream(
                input=state, context=context, stream_mode="custom"
            ):
                yield f"data: {json.dumps(chunk, ensure_ascii=False, default=str)}\n\n"
        except Exception as e:
            error = {"type": "error", "message": str(e)}
            yield f"data: {json.dumps(error, ensure_ascii=False, default=str)}\n\n"
