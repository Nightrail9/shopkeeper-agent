"""
元数据仓库 Mysql 存储
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.entities.column_info import ColumnInfo
from app.entities.column_metric import ColumnMetric
from app.entities.metric_info import MetricInfo
from app.entities.table_info import TableInfo
from app.models.column_info import ColumnInfoMySQL
from app.models.table_info import TableInfoMySQL
from app.repositories.mysql.meta.mappers.column_info_mapper import ColumnInfoMapper
from app.repositories.mysql.meta.mappers.column_metric_mapper import ColumnMetricMapper
from app.repositories.mysql.meta.mappers.metric_info_mapper import MetricInfoMapper
from app.repositories.mysql.meta.mappers.table_info_mapper import TableInfoMapper


class MetaMySQLRepository:
    """
    负责把元数据业务实体持久化到 Meta Mysql 数据库
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    def save_table_infos(self, table_infos: list[TableInfo]):
        """
        批量保存表元数据。输入仍然是业务实体，而不是 ORM 模型
        """
        self.session.add_all([TableInfoMapper.to_model(table) for table in table_infos])

    def save_column_infos(self, column_infos: list[ColumnInfo]):
        """
        批量保存字段元数据。实体到模型的转换统一通过 Mapper 完成
        """
        self.session.add_all(
            [ColumnInfoMapper.to_model(column) for column in column_infos]
        )

    def save_metric_infos(self, metric_infos: list[MetricInfo]):
        """
        批量保存指标元数据。实体到模型的转换统一通过 Mapper 完成
        """
        self.session.add_all(
            [MetricInfoMapper.to_model(metric) for metric in metric_infos]
        )

    def save_column_metrics(self, column_metrics: list[ColumnMetric]):
        """
        批量保存字段指标关联元数据。实体到模型的转换统一通过 Mapper 完成
        """
        self.session.add_all(
            [
                ColumnMetricMapper.to_model(column_metric)
                for column_metric in column_metrics
            ]
        )

    async def get_column_info_by_id(self, column_id: str) -> ColumnInfo | None:
        """
        根据字段 ID 获取字段元数据
        """
        column_info: ColumnInfoMySQL | None = await self.session.get(
            ColumnInfoMySQL, column_id
        )
        if column_info:
            return ColumnInfoMapper.to_entity(column_info)
        else:
            return None

    async def get_key_columns_by_table_id(self, table_id: str) -> list[ColumnInfo]:
        """
        根据表 ID 获取表的所有主键字段和外键字段
        """
        stmt = select(ColumnInfoMySQL).where(
            ColumnInfoMySQL.table_id == table_id,
            ColumnInfoMySQL.role.in_(("primary_key", "foreign_key")),
        )
        result = await self.session.execute(stmt)
        return [ColumnInfoMapper.to_entity(column) for column in result.scalars().all()]
