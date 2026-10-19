"""
字段与指标关联实体
"""

from dataclasses import dataclass


@dataclass
class ColumnMetric:
    """
    字段与指标关联实体
    """

    column_id: str
    metric_id: str
