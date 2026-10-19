"""
TableInfoMapper 映射器
"""

from app.entities.table_info import TableInfo

from app.models.table_info import TableInfoMySQL


class TableInfoMapper:
    """
    负责 `TableInfo` 实体和 `TableInfoMySQL` 模型之间的转换射
    """

    @staticmethod
    def to_entity(table_info_mysql: TableInfoMySQL) -> TableInfo:
        """
        将 `TableInfoMySQL` 模型转换为 `TableInfo` 实体
        """
        return TableInfo(
            id=table_info_mysql.id,
            name=table_info_mysql.name,
            role=table_info_mysql.role,
            description=table_info_mysql.description,
        )

    @staticmethod
    def to_model(table_info: TableInfo) -> TableInfoMySQL:
        """
        将 `TableInfo` 实体转换为 `TableInfoMySQL` 模型
        """
        return TableInfoMySQL(
            id=table_info.id,
            name=table_info.name,
            role=table_info.role,
            description=table_info.description,
        )
