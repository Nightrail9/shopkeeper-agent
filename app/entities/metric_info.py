"""
指标信息实体
"""

from dataclasses import dataclass


@dataclass
class MetricInfo:
    """
    指标信息实体
    """

    id: str
    name: str
    description: str
    # 相关列
    relevant_columns: list[str]
    alias: list[str]
