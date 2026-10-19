"""
`qdrant_client_manager` 客户端管理器
"""

import random
import asyncio
from qdrant_client import AsyncQdrantClient, models
from app.conf.app_config import QdrantConfig, app_config


class QdrantClientManager:
    """
    Qdrant 客户端的初始化和关闭管理
    """

    def __init__(self, qdrant_config: QdrantConfig):
        # 保存配置对象，后面初始化客户端时要从这里读取 host 和 port
        self.qdrant_config = qdrant_config
        # 先把 client 声明出来，真正初始化放到 init() 中进行
        self.client: AsyncQdrantClient | None = None

    def _get_url(self):
        # 根据配置文件拼出 Qdrant 服务地址
        return f"http://{self.qdrant_config.host}:{self.qdrant_config.port}"

    def init(self):
        # 创建异步客户端
        self.client = AsyncQdrantClient(url=self._get_url())

    async def close(self):
        # 项目关闭时统一关闭客户端连接
        if self.client is not None:
            await self.client.close()


qdrant_client_manager = QdrantClientManager(qdrant_config=app_config.qdrant)


if __name__ == "__main__":
    # 先初始化客户端，后面的测试逻辑通过它来获取同一套 Qdrant 客户端
    qdrant_client_manager.init()

    async def test():
        # 取出真正的 Qdrant 异步客户端
        client = qdrant_client_manager.client

        if client is not None:
            # 如果集合不存在，就先创建一个集合
            if not await client.collection_exists("my_collection"):
                await client.create_collection(
                    collection_name="my_collection",
                    vectors_config=models.VectorParams(
                        # 当前集合中的向量维度是 10
                        size=10,
                        # 使用余弦相似度作为距离计算方式
                        distance=models.Distance.COSINE,
                    ),
                )

            # 向集合中写入 10 个随机 point
            await client.upsert(
                collection_name="my_collection",
                points=[
                    models.PointStruct(
                        id=i,
                        vector=[random.random() for _ in range(10)],
                    )
                    for i in range(100)
                ],
            )

            # 用一个随机生成的查询向量做相似度检索
            res = await client.query_points(
                collection_name="my_collection",
                query=[random.random() for _ in range(10)],  # type: ignore
                limit=10,
                score_threshold=0.8,
            )

            # 打印查询结果
            print(res)

    asyncio.run(test())
