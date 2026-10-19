"""
表格信息实体
"""

from dataclasses import dataclass


@dataclass
class TableInfo:
    """
    表格信息实体
    """

    id: str
    name: str
    role: str
    description: str
