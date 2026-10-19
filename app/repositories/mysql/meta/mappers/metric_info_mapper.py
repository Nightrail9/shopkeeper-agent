"""
MetricInfo 映射器
"""

from app.entities.metric_info import MetricInfo
from app.models.metric_info import MetricInfoMySQL


class MetricInfoMapper:
    """
    负责 `MetricInfo` 实体和 `MetricInfoMySQL` 模型之间的转换射
    """

    @staticmethod
    def to_entity(metric_info_mysql: MetricInfoMySQL) -> MetricInfo:
        """
        将 `MetricInfoMySQL` 模型转换为 `MetricInfo` 实体
        """
        return MetricInfo(
            id=metric_info_mysql.id,
            name=metric_info_mysql.name,
            description=metric_info_mysql.description,
            relevant_columns=metric_info_mysql.relevant_columns,
            alias=metric_info_mysql.alias,
        )

    @staticmethod
    def to_model(metric_info: MetricInfo) -> MetricInfoMySQL:
        """
        将 `MetricInfo` 实体转换为 `MetricInfoMySQL` 模型
        """
        return MetricInfoMySQL(
            id=metric_info.id,
            name=metric_info.name,
            description=metric_info.description,
            relevant_columns=metric_info.relevant_columns,
            alias=metric_info.alias,
        )
