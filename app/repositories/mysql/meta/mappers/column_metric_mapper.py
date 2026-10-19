"""
ColumnMetric 映射器
"""

from app.entities.column_metric import ColumnMetric
from app.models.column_metric import ColumnMetricMySQL


class ColumnMetricMapper:
    """
    负责 `ColumnMetric` 实体和 `ColumnMetricMySQL` 模型之间的转换射
    """

    @staticmethod
    def to_entity(column_metric_mysql: ColumnMetricMySQL) -> ColumnMetric:
        """
        将 `ColumnMetricMySQL` 模型转换为 `ColumnMetric` 实体
        """
        return ColumnMetric(
            column_id=column_metric_mysql.column_id,
            metric_id=column_metric_mysql.metric_id,
        )

    @staticmethod
    def to_model(column_metric: ColumnMetric) -> ColumnMetricMySQL:
        """
        将 `ColumnMetric` 实体转换为 `ColumnMetricMySQL` 模型
        """
        return ColumnMetricMySQL(
            column_id=column_metric.column_id,
            metric_id=column_metric.metric_id,
        )
