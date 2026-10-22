"""
召回字段取值节点
"""

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.llm import llm
from app.agent.state import DataAgentState
from app.core.log import logger
from app.entities.value_info import ValueInfo
from app.prompt.prompt_loader import load_prompt


async def recall_value(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    """
    召回和用户问题相关的字段取值
    """
    step = "召回字段取值"
    writer = runtime.stream_writer
    writer({"type": "progress", "step": step, "status": "running"})

    try:
        query = state["query"]
        keywords = state["keywords"]

        value_es_repository = runtime.context["value_es_repository"]

        prompt = PromptTemplate(
            template=load_prompt("extend_keywords_for_value_recall"),
            input_variables=["query"],
        )

        output_parser = JsonOutputParser()
        chain = prompt | llm | output_parser

        result = chain.invoke({"query": query})
        keywords = set(keywords + result)

        value_info_map: dict[str, ValueInfo] = {}
        for keyword in keywords:
            current_value_infos: list[ValueInfo] = await value_es_repository.search(
                keyword
            )
            for value_info in current_value_infos:
                # 以取值 ID 去重，多个关键词可能召回同一条取值
                if value_info.id not in value_info_map:
                    value_info_map[value_info.id] = value_info

        retrieved_value_infos: list[ValueInfo] = list(value_info_map.values())
        logger.info(f"检索到的字段取值: {list(value_info_map.keys())}")
        writer({"type": "progress", "step": step, "status": "success"})
        return {"retrieved_value_infos": retrieved_value_infos}
    except Exception as e:
        logger.error(f"{step}失败: {e}")
        writer({"type": "progress", "step": step, "status": "error"})
        raise
