"""
召回信息合并节点
"""

from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.state import (
    DataAgentState,
    ColumnInfoState,
    MetricInfoState,
    TableInfoState,
)
from app.core.log import logger
from app.entities.column_info import ColumnInfo
from app.entities.metric_info import MetricInfo
from app.entities.table_info import TableInfo
from app.entities.value_info import ValueInfo


async def merge_retrieved_info(
    state: DataAgentState,
    runtime: Runtime[DataAgentContext],
):
    """
    合并召回信息, 并输出SQL生成前的候选表信息和指标信息
    """
    writer = runtime.stream_writer
    step = "合并召回信息"
    writer({"type": "progress", "step": step, "status": "running"})

    try:
        retrieved_column_infos: list[ColumnInfo] = state["retrieved_column_infos"]
        retrieved_metric_infos: list[MetricInfo] = state["retrieved_metric_infos"]
        retrieved_value_infos: list[ValueInfo] = state["retrieved_value_infos"]

        meta_mysql_repository = runtime.context["meta_mysql_repository"]

        # 1. 以 column_id 为键, 合并 column_info
        retrieved_column_infos_map: dict[str, ColumnInfo] = {
            retrieved_column_info.id: retrieved_column_info
            for retrieved_column_info in retrieved_column_infos
        }

        # 2. 补齐指标依赖字段
        for retrieved_metric_info in retrieved_metric_infos:
            for relevant_column in retrieved_metric_info.relevant_columns:
                if relevant_column not in retrieved_column_infos_map:
                    column_info: ColumnInfo | None = (
                        await meta_mysql_repository.get_column_info_by_id(
                            relevant_column
                        )
                    )
                    if column_info is None:
                        logger.warning(f"指标依赖字段不存在: {relevant_column}")
                        continue
                    retrieved_column_infos_map[relevant_column] = column_info

        # 3. 把字段取值合并回字段 examples
        for retrieved_value_info in retrieved_value_infos:
            value = retrieved_value_info.value
            column_id = retrieved_value_info.column_id
            if column_id not in retrieved_column_infos_map:
                column_info: ColumnInfo | None = (
                    await meta_mysql_repository.get_column_info_by_id(column_id)
                )
                if column_info is None:
                    logger.warning(f"字段取值对应的字段不存在: {column_id}")
                    continue
                retrieved_column_infos_map[column_id] = column_info
            if value not in retrieved_column_infos_map[column_id].examples:
                retrieved_column_infos_map[column_id].examples.append(value)

        # 4. 按表组织字段上下文
        table_to_columns_map: dict[str, list[ColumnInfo]] = {}
        for column_info in retrieved_column_infos_map.values():
            table_id = column_info.table_id
            if table_id not in table_to_columns_map:
                table_to_columns_map[table_id] = []
            table_to_columns_map[table_id].append(column_info)

        # 5. 补齐主外键字段
        for table_id in table_to_columns_map.keys():
            key_columns: list[ColumnInfo] = (
                await meta_mysql_repository.get_key_columns_by_table_id(table_id)
            )
            column_ids = [
                column_info.id for column_info in table_to_columns_map[table_id]
            ]
            for key_column in key_columns:
                if key_column.id not in column_ids:
                    table_to_columns_map[table_id].append(key_column)

        # 6. 生成表结构上下文
        table_infos: list[TableInfoState] = []
        for table_id, column_infos in table_to_columns_map.items():
            table_info: TableInfo | None = (
                await meta_mysql_repository.get_table_info_by_id(table_id)
            )
            if table_info is None:
                logger.warning(f"字段对应的表不存在: {table_id}")
                continue
            columns = [
                ColumnInfoState(
                    name=column_info.name,
                    type=column_info.type,
                    role=column_info.role,
                    examples=column_info.examples,
                    description=column_info.description,
                    alias=column_info.alias,
                    table_id=column_info.table_id,
                )
                for column_info in column_infos
            ]
            table_info_state = TableInfoState(
                name=table_info.name,
                role=table_info.role,
                description=table_info.description,
                columns=columns,
            )
            table_infos.append(table_info_state)

        # 7. 生成指标上下文
        metric_infos: list[MetricInfoState] = [
            MetricInfoState(
                name=retrieved_metric_info.name,
                description=retrieved_metric_info.description,
                relevant_columns=retrieved_metric_info.relevant_columns,
                alias=retrieved_metric_info.alias,
            )
            for retrieved_metric_info in retrieved_metric_infos
        ]

        logger.info(
            f"合并后的表信息: {[table_info['name'] for table_info in table_infos]}"
        )
        logger.info(
            f"合并后的指标信息: {[metric_info['name'] for metric_info in metric_infos]}"
        )

        writer({"type": "progress", "step": step, "status": "success"})
        return {
            "table_infos": table_infos,
            "metric_infos": metric_infos,
        }
    except Exception as e:
        logger.error(f"{step} 合并信息失败: {e}")
        writer({"type": "progress", "step": step, "status": "error"})
        raise
