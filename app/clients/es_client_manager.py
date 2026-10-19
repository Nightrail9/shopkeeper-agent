"""
`es_client_manager` 客户端管理器
"""

import asyncio

from elasticsearch import AsyncElasticsearch

from app.conf.app_config import ESConfig, app_config


class ESClientManager:
    """
    Elasticsearch 客户端的生命周期管理
    """

    def __init__(self, es_config: ESConfig):
        # 保存 ES 配置对象，后面初始化客户端时会从这里读取 host 和 port
        self.es_config = es_config
        # 先把 client 声明出来，真正初始化放到 init() 中进行
        self.client: AsyncElasticsearch | None = None

    def _get_url(self):
        # 根据配置文件拼出 Elasticsearch 服务地址
        return f"http://{self.es_config.host}:{self.es_config.port}"

    def init(self):
        # 创建异步客户端
        self.client = AsyncElasticsearch(hosts=[self._get_url()])

    async def close(self):
        # 项目关闭时统一关闭客户端连接
        if self.client is not None:
            await self.client.close()


es_client_manager = ESClientManager(es_config=app_config.es)

if __name__ == "__main__":
    # 先初始化客户端，后面的测试逻辑通过它来获取同一套 Elasticsearch 客户端
    es_client_manager.init()

    async def test():
        # 取出真正的 Elasticsearch 异步客户端
        client = es_client_manager.client

        if client is not None:
            # 索引可能由上一次运行创建；存在时复用，避免重复创建时报 400。
            if not await client.indices.exists(index="my-books"):
                await client.indices.create(
                    index="my-books",
                    mappings={
                        "dynamic": False,
                        "properties": {
                            # 书名和作者适合做全文检索，所以用 text 类型
                            "name": {"type": "text"},
                            "author": {"type": "text"},
                            # 日期适合做范围查询，所以用 date 类型
                            "release_date": {
                                "type": "date",
                                "format": "yyyy-MM-dd",
                            },
                            # 页数适合做数值范围查询，所以用 integer 类型
                            "page_count": {"type": "integer"},
                        },
                    },
                )

            # 固定文档 ID，重复运行时覆盖同一文档而不是不断追加副本。
            await client.bulk(
                operations=[
                    {"index": {"_index": "my-books", "_id": "book-1"}},
                    {
                        "name": "Revelation Space",
                        "author": "Alastair Reynolds",
                        "release_date": "2000-03-15",
                        "page_count": 585,
                    },
                    {"index": {"_index": "my-books", "_id": "book-2"}},
                    {
                        "name": "1984",
                        "author": "George Orwell",
                        "release_date": "1985-06-01",
                        "page_count": 328,
                    },
                    {"index": {"_index": "my-books", "_id": "book-3"}},
                    {
                        "name": "Fahrenheit 451",
                        "author": "Ray Bradbury",
                        "release_date": "1953-10-15",
                        "page_count": 227,
                    },
                    {"index": {"_index": "my-books", "_id": "book-4"}},
                    {
                        "name": "Brave New World",
                        "author": "Aldous Huxley",
                        "release_date": "1932-06-01",
                        "page_count": 268,
                    },
                    {"index": {"_index": "my-books", "_id": "book-5"}},
                    {
                        "name": "The Handmaids Tale",
                        "author": "Margaret Atwood",
                        "release_date": "1985-06-01",
                        "page_count": 311,
                    },
                ],
            )

            # 做一个简单的全文检索
            res = await client.search(
                index="my-books", query={"match": {"name": "brave"}}
            )

            # 打印检索结果
            print(res)

    # 运行测试并确保客户端始终关闭。
    async def run_test():
        try:
            await test()
        finally:
            # 连接请求失败时也必须释放 aiohttp session。
            await es_client_manager.close()

    asyncio.run(run_test())
