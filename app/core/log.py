"""
日志管理器
"""

import sys
from pathlib import Path

from loguru import logger

from app.conf.app_config import app_config
from app.core.context import request_id_ctx_var

# 日志格式
log_format = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
    "<level>{level: <8}</level> | "
    "<magenta>request_id - {extra[request_id]}</magenta> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
    "<level>{message}</level>"
)


def inject_request_id(record):
    """
    注入请求ID到日志记录中
    """
    request_id = request_id_ctx_var.get()
    record["extra"]["request_id"] = request_id


# 移除默认的输出
logger.remove()

# 全局注入请求ID到所有模块的日志记录中
logger.configure(patcher=inject_request_id)

# 添加控制台输出
if app_config.logging.console.enable:
    logger.add(
        sys.stdout,
        format=log_format,
        level=app_config.logging.console.level,
    )

# 添加文件输出
if app_config.logging.file.enable:
    path = Path(app_config.logging.file.path)
    path.mkdir(parents=True, exist_ok=True)
    logger.add(
        sink=path / "app.log",
        format=log_format,
        level=app_config.logging.file.level,
        rotation=app_config.logging.file.rotation,
        retention=app_config.logging.file.retention,
        encoding="utf-8",
    )
