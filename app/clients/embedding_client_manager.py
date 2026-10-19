"""
`embedding_client_manager` 客户端管理器
"""

import asyncio

import httpx
from langchain_openai import OpenAIEmbeddings
from pydantic import SecretStr

from app.conf.app_config import EmbeddingConfig, app_config


class EmbeddingClientManager:
    """
    Embedding 客户端的初始化和关闭管理
    """

    def __init__(self, config: EmbeddingConfig):
        self.client: OpenAIEmbeddings | None = None
        self.config = config
        self._http_client: httpx.Client | None = None
        self._http_async_client: httpx.AsyncClient | None = None

    def _get_url(self) -> str:
        """拼接 Embedding 服务地址"""
        return f"http://{self.config.host}:{self.config.port}/v1"

    def init(self):
        # TEI 本地服务不校验密钥，api_key 传占位值即可
        self._http_client = httpx.Client(trust_env=False)
        self._http_async_client = httpx.AsyncClient(trust_env=False)
        self.client = OpenAIEmbeddings(
            model=self.config.model,
            base_url=self._get_url(),
            api_key=SecretStr("EMPTY"),
            check_embedding_ctx_length=False,
            http_client=self._http_client,
            http_async_client=self._http_async_client,
        )

    async def close(self):
        # 项目关闭时统一释放底层的 httpx 连接
        if self._http_async_client is not None:
            await self._http_async_client.aclose()
        if self._http_client is not None:
            self._http_client.close()


# 模块级单例，供其他模块按需复用同一个客户端管理器
embedding_client_manager = EmbeddingClientManager(app_config.embedding)


if __name__ == "__main__":
    embedding_client_manager.init()
    client = embedding_client_manager.client

    async def test_embedding():
        if client is not None:
            text = "What is deep learning?"
            query_result = await client.aembed_query(text)
            # 只打印前三个维度
            print("Embedding result (first 3 dimensions):", query_result[:3])
        else:
            print("Client is not initialized.")

    asyncio.run(test_embedding())
