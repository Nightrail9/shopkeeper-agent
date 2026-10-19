import asyncio

from qdrant_client import AsyncQdrantClient, models

QDRANT_URL = "http://localhost:6333"
COLLECTION_NAME = "quickstart_demo"
VECTOR_DIM = 4


async def recreate_collection(client):
    """为了让示例能够重复运行，我们先删除集合，再创建一个新集合。"""
    if await client.collection_exists(COLLECTION_NAME):
        await client.delete_collection(COLLECTION_NAME)

    # 创建集合
    await client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=models.VectorParams(
            size=VECTOR_DIM,
            distance=models.Distance.COSINE,
        ),
    )
    print(f"集合 {COLLECTION_NAME} 创建成功，维度为 {VECTOR_DIM} 维")


async def add_vectors(client):
    """
    写入几个示例向量到集合

    这里同时带上 payload 字段，方便读者理解：
    在 Qdrant 中，一个 point 不只有 vector， 还可以有其他字段，比如 id、name、description 等。
    """
    await client.upsert(
        collection_name=COLLECTION_NAME,
        points=[
            models.PointStruct(
                id=1,
                vector=[0.05, 0.61, 0.76, 0.74],
                payload={"name": "订单分析", "type": "report"},
            ),
            models.PointStruct(
                id=2,
                vector=[0.19, 0.81, 0.75, 0.11],
                payload={"name": "销量趋势", "type": "metric"},
            ),
            models.PointStruct(
                id=3,
                vector=[0.36, 0.55, 0.47, 0.94],
                payload={"name": "区域销售额", "type": "dimension"},
            ),
        ],
    )
    print("2. 已写入 3 个向量点。")


async def run_query(client):
    """
    执行一次向量查询

    查询向量就和集合里的点做余弦相似度计算，
    最终返回最相近的点。
    """
    query_vector = [0.2, 0.3, 0.4, 0.5]
    result = await client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
    )

    print(f"3. 查询向量：{query_vector}")
    print(f"4. 查询结果：")
    for i, point in enumerate(result.points, start=1):
        print(f"({i}) id={point.id}, score={point.score:.4f}, payload={point.payload}")


async def main():
    # 直接初始化客户端，方便单独学习 quickstart 的基本用法
    client = AsyncQdrantClient(url=QDRANT_URL)

    try:
        await recreate_collection(client)
        await add_vectors(client)
        await run_query(client)
    except Exception as e:
        print(f"发生错误：{e}")
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
