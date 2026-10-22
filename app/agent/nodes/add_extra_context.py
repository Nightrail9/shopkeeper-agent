"""
额外上下文补全节点
"""

from datetime import date

from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState, DateInfoState, DBInfoState
from app.core.log import logger


async def add_extra_context(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    """
    补齐 SQL 生成所需的日期和数据库环境信息
    """
    writer = runtime.stream_writer
    step = "添加额外上下文"
    writer({"type": "progress", "step": step, "status": "running"})
    try:
        dw_mysql_repository = runtime.context["dw_mysql_repository"]

        today = date.today()
        date_str = today.strftime("%Y-%m-%d")
        weekday = today.strftime("%A")
        quarter = f"Q{(today.month-1)//3+1}"
        date_info = DateInfoState(
            date=date_str,
            weekday=weekday,
            quarter=quarter,
        )

        db = await dw_mysql_repository.get_db_info()
        db_info = DBInfoState(**db)
        logger.info(f"数据库环境信息: {db_info}")
        logger.info(f"日期信息: {date_info}")

        writer({"type": "progress", "step": step, "status": "success"})
        return {"date_info": date_info, "db_info": db_info}

    except Exception as e:
        logger.error(f"{step} 添加额外上下文失败: {e}")
        writer({"type": "progress", "step": step, "status": "error"})
        raise
