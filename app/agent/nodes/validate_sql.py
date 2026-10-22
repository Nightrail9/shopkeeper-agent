"""
SQL 校验节点
"""

from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState
from app.core.log import logger
from app.repositories.mysql.dw.dw_mysql_repository import DWMySQLRepository


async def validate_sql(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    """
    校验 SQL，并返回 error 字段控制后续条件分支
    """
    writer = runtime.stream_writer
    step = "校验 SQL"
    writer({"type": "progress", "step": step, "status": "running"})

    try:
        sql = state["sql"]
        dw_mysql_repository: DWMySQLRepository = runtime.context["dw_mysql_repository"]
        try:
            await dw_mysql_repository.validate(sql)
            writer({"type": "progress", "step": step, "status": "success"})
            logger.info("SQL 语法正确")
            return {"error": None}
        except Exception as e:
            logger.error(f"SQL 语法错误: {str(e)}")
            writer({"type": "progress", "step": step, "status": "success"})
            return {"error": str(e)}
    except Exception as e:
        logger.error(f"{step} SQL 校验失败: {e}")
        writer({"type": "progress", "step": step, "status": "error"})
        raise
