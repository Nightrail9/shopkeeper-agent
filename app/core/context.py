"""
上下文管理器
"""

from contextvars import ContextVar

# 使用 ContextVar 而不是全局变量，是为了在多线程环境下保持上下文独立性
request_id_ctx_var: ContextVar[str] = ContextVar("request_id", default="1")
