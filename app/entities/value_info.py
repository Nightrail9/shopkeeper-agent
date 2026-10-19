"""
字段取值业务实体
"""

from dataclasses import dataclass


@dataclass
class ValueInfo:
    """
    字段取值业务实体
    """

    id: str
    value: str
    column_id: str
