"""
指标信息过滤节点
"""

import yaml
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.llm import llm
from app.agent.state import DataAgentState, MetricInfoState
from app.core.log import logger
from app.prompt.prompt_loader import load_prompt


async def filter_metric(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    """
    根据用户问题裁剪候选指标上下文
    """
    writer = runtime.stream_writer
    step = "过滤指标信息"
    writer({"type": "progress", "step": step, "status": "running"})

    try:
        query = state["query"]
        metric_infos: list[MetricInfoState] = state["metric_infos"]

        prompt = PromptTemplate(
            template=load_prompt("filter_metric_info"),
            input_variables=["query", "metric_infos"],
        )

        output_parser = JsonOutputParser()
        chain = prompt | llm | output_parser

        result = await chain.ainvoke(
            {
                "query": query,
                "metric_infos": yaml.dump(
                    metric_infos,
                    allow_unicode=True,
                    sort_keys=False,
                ),
            }
        )
        filtered_metric_infos: list[MetricInfoState] = [
            metric_info for metric_info in metric_infos if metric_info["name"] in result
        ]

        logger.info(
            f"过滤后的指标信息: {[metric_info['name'] for metric_info in filtered_metric_infos]}"
        )
        writer({"type": "progress", "step": step, "status": "success"})
        return {"metric_infos": filtered_metric_infos}
    except Exception as e:
        logger.error(f"{step} 过滤指标信息失败: {e}")
        writer({"type": "progress", "step": step, "status": "error"})
        raise
