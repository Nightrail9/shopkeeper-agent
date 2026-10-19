"""
`mysql_client_manager` 客户端管理器
"""

import asyncio

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)

from app.conf.app_config import DBConfig, app_config


class MysqlClientManager:
    """
    管理 MySQL Engine 和 Session 工厂
    """

    def __init__(self, config: DBConfig):
        self.engine: AsyncEngine | None = None
        self.session_factory: async_sessionmaker[AsyncSession] | None = None
        self.config = config

    def _get_url(self) -> str:
        """
        拼接 MySQL 异步连接地址
        """
        return f"mysql+asyncmy://{self.config.user}:{self.config.password}@{self.config.host}:{self.config.port}/{self.config.database}?charset=utf8mb4"

    def init(self):
        """
        初始化 Engine 和 Session 工厂
        """
        self.engine = create_async_engine(
            self._get_url(),
            pool_size=10,
            pool_pre_ping=True,
        )
        self.session_factory = async_sessionmaker(
            self.engine,
            expire_on_commit=False,
        )

    async def close(self):
        """
        关闭 Engine 连接池
        """
        if self.engine is not None:
            await self.engine.dispose()


meta_mysql_client_manager = MysqlClientManager(app_config.db_meta)
dw_mysql_client_manager = MysqlClientManager(app_config.db_dw)


if __name__ == "__main__":
    dw_mysql_client_manager.init()

    async def test():
        """
        执行一次简单查询，验证 Mysql 连接与结果结构
        """
        async with dw_mysql_client_manager.session_factory() as session:
            sql = "select * from fact_order limit 10"
            result = await session.execute(text(sql))
            rows = result.mappings().all()
            print(type(rows))
            print(type(rows[0]))
            print(rows[0]["order_id"])

    asyncio.run(test())
