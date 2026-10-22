"""
元数据知识构建配置
"""

from dataclasses import dataclass


@dataclass
class ColumnConfig:
    """
    单个字段的同步配置
    """

    name: str
    role: str
    description: str
    alias: list[str]
    sync: bool


@dataclass
class TableConfig:
    """
    表格同步配置
    """

    name: str
    role: str
    description: str
    columns: list[ColumnConfig]


@dataclass
class MetricConfig:
    """
    单个指标同步配置
    """

    name: str
    description: str
    relevant_columns: list[str]
    alias: list[str]


@dataclass
class MetaConfig:
    """
    元数据知识构建总配置
    """

    tables: list[TableConfig] | None = None
    metrics: list[MetricConfig] | None = None
