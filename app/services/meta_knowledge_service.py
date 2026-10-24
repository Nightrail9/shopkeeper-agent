"""
元数据知识构建服务
"""

import uuid
from dataclasses import asdict
from datetime import date, datetime
from pathlib import Path

from langchain_core.embeddings import Embeddings
from omegaconf import OmegaConf
from sqlalchemy import delete

from app.conf.meta_config import MetaConfig
from app.core.log import logger
from app.entities.column_info import ColumnInfo
from app.entities.column_metric import ColumnMetric
from app.entities.metric_info import MetricInfo
from app.entities.table_info import TableInfo
from app.entities.value_info import ValueInfo
from app.models.column_info import ColumnInfoMySQL
from app.models.column_metric import ColumnMetricMySQL
from app.models.metric_info import MetricInfoMySQL
from app.models.table_info import TableInfoMySQL
from app.repositories.es.value_es_repository import ValueESRepository
from app.repositories.mysql.dw.dw_mysql_repository import DWMySQLRepository
from app.repositories.mysql.meta.meta_mysql_repository import MetaMySQLRepository
from app.repositories.qdrant.column_qdrant_repository import ColumnQdrantRepository
from app.repositories.qdrant.metric_qdrant_repository import MetricQdrantRepository


class MetaKnowledgeService:
    """
    负责串联元数据知识构建流程的应用服务
    """

    def __init__(
        self,
        meta_mysql_repository: MetaMySQLRepository,
        dw_mysql_repository: DWMySQLRepository,
        column_qdrant_repository: ColumnQdrantRepository,
        embedding_client: Embeddings,
        value_es_repository: ValueESRepository,
        metric_qdrant_repository: MetricQdrantRepository,
    ):
        self.meta_mysql_repository = meta_mysql_repository
        self.dw_mysql_repository = dw_mysql_repository
        self.column_qdrant_repository = column_qdrant_repository
        self.embedding_client = embedding_client
        self.value_es_repository = value_es_repository
        self.metric_qdrant_repository = metric_qdrant_repository

    async def _save_tables_to_meta_db(
        self,
        meta_config: MetaConfig,
    ) -> list[ColumnInfo]:
        """
        把元数据配置中的表元数据保存到 Meta Mysql 数据库
        """

        table_infos: list[TableInfo] = []
        column_infos: list[ColumnInfo] = []

        for table in meta_config.tables:
            table_info = TableInfo(
                id=table.name,
                name=table.name,
                role=table.role,
                description=table.description,
            )
            table_infos.append(table_info)

            column_types = await self.dw_mysql_repository.get_column_types(table.name)

            for column in table.columns:
                if column.name not in column_types:
                    raise ValueError(
                        f"配置中的字段 '{table.name}.{column.name}' 在数据仓库表中不存在，"
                        f"请检查 conf/meta_config.yaml 中的列名是否拼写正确"
                    )

                column_values = await self.dw_mysql_repository.get_column_values(
                    table.name, column.name
                )

                column_info = ColumnInfo(
                    id=f"{table.name}.{column.name}",
                    name=column.name,
                    type=column_types[column.name],
                    role=column.role,
                    examples=column_values,
                    description=column.description,
                    alias=column.alias,
                    table_id=table.name,
                )
                column_infos.append(column_info)
        async with self.meta_mysql_repository.session.begin():
            # 先清空旧数据，避免重复运行时主键冲突
            await self.meta_mysql_repository.session.execute(delete(ColumnInfoMySQL))
            await self.meta_mysql_repository.session.execute(delete(TableInfoMySQL))
            self.meta_mysql_repository.save_table_infos(table_infos)
            self.meta_mysql_repository.save_column_infos(column_infos)

        return column_infos

    async def _embed_and_upsert(
        self,
        points: list[dict],
        repository: ColumnQdrantRepository | MetricQdrantRepository,
    ):
        """
        批量生成 embedding 并写入 Qdrant 的公共逻辑
        """
        embeddings: list[list[float]] = []
        embeddings_texts = [point["embedding_text"] for point in points]
        embeddings_batch_size = 4
        for i in range(0, len(embeddings_texts), embeddings_batch_size):
            batch_embeddings_texts = embeddings_texts[i : i + embeddings_batch_size]
            batch_embeddings = await self.embedding_client.aembed_documents(
                batch_embeddings_texts
            )
            embeddings.extend(batch_embeddings)

        ids = [point["id"] for point in points]
        payloads = [point["payload"] for point in points]

        await repository.upsert(
            ids=ids,
            embeddings=embeddings,
            payloads=payloads,
        )

    async def _save_columns_info_to_qdrant(
        self,
        column_infos: list[ColumnInfo],
    ):
        """
        把元数据配置中的字段元数据保存到 Qdrant 数据库
        """
        # 删除旧 collection 以避免重复运行产生脏数据
        if await self.column_qdrant_repository.client.collection_exists(
            collection_name=self.column_qdrant_repository.collection_name
        ):
            await self.column_qdrant_repository.client.delete_collection(
                collection_name=self.column_qdrant_repository.collection_name
            )
        await self.column_qdrant_repository.ensure_collection()

        points: list[dict] = []
        for column_info in column_infos:
            points.append(
                {
                    "id": str(uuid.uuid4()),
                    "embedding_text": column_info.name,
                    "payload": asdict(column_info),
                }
            )

            points.append(
                {
                    "id": str(uuid.uuid4()),
                    "embedding_text": column_info.description,
                    "payload": asdict(column_info),
                }
            )

            for alias in column_info.alias:
                points.append(
                    {
                        "id": str(uuid.uuid4()),
                        "embedding_text": alias,
                        "payload": asdict(column_info),
                    }
                )

        await self._embed_and_upsert(points, self.column_qdrant_repository)

    async def _save_values_info_to_es(
        self,
        meta_config: MetaConfig,
        column_infos: list[ColumnInfo],
    ):
        """
        把元数据配置中的字段值保存到 Elasticsearch 数据库
        """
        # 删除旧索引以避免重复运行产生脏数据
        if await self.value_es_repository.client.indices.exists(
            index=self.value_es_repository.index_name
        ):
            await self.value_es_repository.client.indices.delete(
                index=self.value_es_repository.index_name
            )
        await self.value_es_repository.ensure_index()

        column2sync: dict[str, bool] = {}
        for table in meta_config.tables:
            for column in table.columns:
                column2sync[f"{table.name}.{column.name}"] = column.sync

        value_infos: list[ValueInfo] = []
        for column_info in column_infos:
            sync = column2sync[column_info.id]
            if sync:
                current_column_values = (
                    await self.dw_mysql_repository.get_column_values(
                        column_info.table_id, column_info.name, 100000
                    )
                )
                for current_column_value in current_column_values:
                    if current_column_value is None:
                        continue
                    # 将日期/日期时间类型转换为 ISO 格式字符串，其余保持 str()
                    if isinstance(current_column_value, (date, datetime)):
                        value_str = current_column_value.isoformat()
                    else:
                        value_str = str(current_column_value)
                    value_infos.append(
                        ValueInfo(
                            id=f"{column_info.id}.{value_str}",
                            column_id=column_info.id,
                            value=value_str,
                        )
                    )
        await self.value_es_repository.index(value_infos)

    async def _save_metrics_to_meta_db(
        self,
        meta_config: MetaConfig,
        column_infos: list[ColumnInfo],
    ) -> list[MetricInfo]:
        """
        把元数据配置中的指标保存到元数据库
        """
        # 校验 relevant_columns 引用的列是否已配置
        valid_column_ids = {column_info.id for column_info in column_infos}
        for metric in meta_config.metrics:
            for column_id in metric.relevant_columns:
                if column_id not in valid_column_ids:
                    raise ValueError(
                        f"指标 '{metric.name}' 的 relevant_columns 引用了未配置的字段 '{column_id}'，"
                        f"请检查 conf/meta_config.yaml 中的列名是否拼写正确"
                    )

        metric_infos: list[MetricInfo] = []
        column_metrics: list[ColumnMetric] = []

        for metric in meta_config.metrics:
            metric_info = MetricInfo(
                id=metric.name,
                name=metric.name,
                description=metric.description,
                relevant_columns=metric.relevant_columns,
                alias=metric.alias,
            )
            metric_infos.append(metric_info)
            for column in metric.relevant_columns:
                column_metrics.append(
                    ColumnMetric(
                        metric_id=metric.name,
                        column_id=column,
                    )
                )

        async with self.meta_mysql_repository.session.begin():
            # 先清空旧数据，避免重复运行时主键冲突
            await self.meta_mysql_repository.session.execute(delete(ColumnMetricMySQL))
            await self.meta_mysql_repository.session.execute(delete(MetricInfoMySQL))
            self.meta_mysql_repository.save_metric_infos(metric_infos)
            self.meta_mysql_repository.save_column_metrics(column_metrics)

        return metric_infos

    async def _save_metrics_to_qdrant(
        self,
        metric_infos: list[MetricInfo],
    ):
        """
        把元数据配置中的指标保存到 Qdrant 数据库
        """
        # 删除旧 collection 以避免重复运行产生脏数据
        if await self.metric_qdrant_repository.client.collection_exists(
            collection_name=self.metric_qdrant_repository.collection_name
        ):
            await self.metric_qdrant_repository.client.delete_collection(
                collection_name=self.metric_qdrant_repository.collection_name
            )
        await self.metric_qdrant_repository.ensure_collection()

        points: list[dict] = []
        for metric_info in metric_infos:
            points.append(
                {
                    "id": str(uuid.uuid4()),
                    "embedding_text": metric_info.name,
                    "payload": asdict(metric_info),
                }
            )

            points.append(
                {
                    "id": str(uuid.uuid4()),
                    "embedding_text": metric_info.description,
                    "payload": asdict(metric_info),
                }
            )

            for alias in metric_info.alias:
                points.append(
                    {
                        "id": str(uuid.uuid4()),
                        "embedding_text": alias,
                        "payload": asdict(metric_info),
                    }
                )

        await self._embed_and_upsert(points, self.metric_qdrant_repository)

    async def build(
        self,
        config_path: Path,
    ):
        """
        构建指标索引
        """
        context = OmegaConf.load(config_path)
        schema = OmegaConf.structured(MetaConfig)
        meta_config: MetaConfig = OmegaConf.to_object(OmegaConf.merge(schema, context))

        if meta_config.tables:
            column_infos = await self._save_tables_to_meta_db(meta_config)
            logger.info("保存表格信息和字段信息到 Meta MySQL 数据库")

            await self._save_columns_info_to_qdrant(column_infos)
            logger.info("为字段信息建立向量索引")

            await self._save_values_info_to_es(meta_config, column_infos)
            logger.info("为字段值建立全文索引")

        if meta_config.metrics:
            if not meta_config.tables:
                raise ValueError(
                    "配置中存在 metrics 但缺少 tables，"
                    "relevant_columns 校验依赖已配置的字段信息"
                )
            metric_infos = await self._save_metrics_to_meta_db(
                meta_config, column_infos
            )
            logger.info("保存指标信息到 Meta MySQL 数据库")

            await self._save_metrics_to_qdrant(metric_infos)
            logger.info("为指标信息建立向量索引")
