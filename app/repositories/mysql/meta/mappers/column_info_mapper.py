"""
ColumnInfo 映射器
"""

from app.entities.column_info import ColumnInfo
from app.models.column_info import ColumnInfoMySQL


class ColumnInfoMapper:
    """
    负责 `ColumnInfo` 实体和 `ColumnInfoMySQL` 模型之间的转换射
    """

    @staticmethod
    def to_entity(column_info_mysql: ColumnInfoMySQL) -> ColumnInfo:
        """
        将 `ColumnInfoMySQL` 模型转换为 `ColumnInfo` 实体
        """
        return ColumnInfo(
            id=column_info_mysql.id,
            name=column_info_mysql.name,
            type=column_info_mysql.type,
            role=column_info_mysql.role,
            examples=column_info_mysql.examples,
            description=column_info_mysql.description,
            alias=column_info_mysql.alias,
            table_id=column_info_mysql.table_id,
        )

    @staticmethod
    def to_model(column_info: ColumnInfo) -> ColumnInfoMySQL:
        """
        将 `ColumnInfo` 实体转换为 `ColumnInfoMySQL` 模型
        """
        return ColumnInfoMySQL(
            id=column_info.id,
            name=column_info.name,
            type=column_info.type,
            role=column_info.role,
            examples=column_info.examples,
            description=column_info.description,
            alias=column_info.alias,
            table_id=column_info.table_id,
        )
