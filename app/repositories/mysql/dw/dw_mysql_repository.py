"""
数据仓库 Mysql 存储
"""

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class DWMySQLRepository:
    """
    负责查询数据仓库真实表结构和字段示例
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_column_types(self, table_name: str) -> dict[str, str]:
        """
        根据表名获取表的所有字段类型
        """
        sql = f"show columns from {table_name}"
        result = await self.session.execute(text(sql))
        result_dict = result.mappings().all()
        return {row["Field"]: row["Type"] for row in result_dict}

    async def get_column_values(
        self, table_name: str, column_name: str, limit: int = 10
    ) -> list:
        """
        根据字段名获取字段示例值
        """
        sql = f"select distinct {column_name} from {table_name} limit {limit}"
        result = await self.session.execute(text(sql))
        return list(result.scalars().all())

    async def get_db_info(self) -> dict[str, str]:
        """
        获取当前数据仓库的方言和版本
        """
        sql = "select version()"
        result = await self.session.execute(text(sql))
        version = result.scalar()

        dialect = self.session.bind.dialect.name
        return {"dialect": dialect, "version": version}

    async def validate(self, sql: str):
        """
        用 explain 验证 SQL 语句是否正确
        """
        sql = f"explain {sql}"
        await self.session.execute(text(sql))

    async def run(self, sql: str) -> list[dict]:
        """
        执行最终 SQL，并把 SQLAlchemy 行对象转换成前端更易消费的字典列表
        """

        result = await self.session.execute(text(sql))
        return [dict(row) for row in result.mappings().all()]
