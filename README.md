# shopkeeper-agent

## 开发环境基础服务

项目根目录执行以下命令启动 MySQL、Elasticsearch、Kibana、Qdrant 和 Embedding 服务：

```bash
docker compose -f docker/docker-compose.yaml config
docker compose -f docker/docker-compose.yaml up -d
```

首次启动 MySQL 时，镜像会自动执行 `docker/mysql/meta.sql` 和 `docker/mysql/dw.sql`，分别创建 `meta` 元数据库和 `dw` 教学数仓。初始化脚本只会在 MySQL 数据目录为空时执行；已有 `mysql_data` 卷不会因脚本更新而自动重建数据库。

Elasticsearch 镜像会基于 `docker/elasticsearch/Dockerfile` 安装 IK 中文分词插件。Embedding 容器从 `docker/embedding/bge-large-zh-v1.5` 读取本地模型；模型权重未纳入 Git。如果该目录缺少完整模型文件，可在项目根目录下载：

```bash
uv run hf download BAAI/bge-large-zh-v1.5 --local-dir docker/embedding/bge-large-zh-v1.5
```

服务端口：MySQL `3306`、Elasticsearch `9200`、Kibana `5601`、Qdrant `6333`/`6334`、Embedding `8081`。

停止容器但保留数据：

```bash
docker compose -f docker/docker-compose.yaml down
```

删除数据卷会永久删除本地数据库和索引数据；非必要不要使用 `down -v`。

## 大模型密钥

复制 `.env.example` 为 `.env`，填写 `LLM_API_KEY`。`.env` 已加入 Git 忽略规则，不要提交真实密钥。当前配置中的 MySQL 密码是仅供本地开发的示例值，不适用于生产环境。
