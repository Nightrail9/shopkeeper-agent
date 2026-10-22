"""
电商问数 Agent 状态定义
"""

from typing import TypedDict, Any

from app.entities.column_info import ColumnInfo
from app.entities.metric_info import MetricInfo
from app.entities.value_info import ValueInfo


class MetricInfoState(TypedDict):
    """
    面向 SQL 生成提示词的指标信息
    """

    name: str
    description: str
    relevant_columns: list[str]
    alias: list[str]


class ColumnInfoState(TypedDict):
    """
    表上下文中的字段信息
    """

    name: str
    type: str
    role: str
    examples: list[Any]
    description: str
    alias: list[str]
    table_id: str


class TableInfoState(TypedDict):
    """
    SQL 生成阶段真正传给模型的表结构上下文信息
    """

    name: str
    role: str
    description: str
    columns: list[ColumnInfoState]


class DateInfoState(TypedDict):
    """
    SQL 生成阶段使用的当前日期上下文信息
    """

    date: str
    weekday: str
    quarter: str


class DBInfoState(TypedDict):
    """
    SQL 生成阶段使用的数据库环境上下文信息
    """

    dialect: str
    version: str


class DataAgentState(TypedDict):
    """
    一次问数链路中的核心状态
    """

    query: str
    keywords: list[str]
    retrieved_column_infos: list[ColumnInfo]
    retrieved_metric_infos: list[MetricInfo]
    retrieved_value_infos: list[ValueInfo]

    table_infos: list[TableInfoState]
    metric_infos: list[MetricInfoState]
    date_info: DateInfoState
    db_info: DBInfoState

    sql: str
    result: list[dict] | None

    # TypedDict 不支持默认值，这里只声明类型；缺失时由各节点显式写回
    error: str | None
