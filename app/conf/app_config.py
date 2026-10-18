from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv
from omegaconf import OmegaConf


# 文件日志配置，对应app_config.yaml中的logging.file
@dataclass
class File:
    enable: bool
    level: str
    path: str
    rotation: str
    retention: str


# 控制台日志配置，对应app_config.yaml中的logging.console
@dataclass
class Console:
    enable: bool
    level: str


# 日志配置
@dataclass
class LoggingConfig:
    file: File
    console: Console


# 数据库配置
@dataclass
class DBConfig:
    host: str
    port: int
    user: str
    password: str
    database: str


# Qdrant配置，对应app_config.yaml中的qdrant
@dataclass
class QdrantConfig:
    host: str
    port: int
    embedding_size: int


# 嵌入模型配置，对应app_config.yaml中的embedding
@dataclass
class EmbeddingConfig:
    host: str
    port: int
    model: str
    container_name: str
    startup_timeout: int


# Elasticsearch配置，对应app_config.yaml中的elasticsearch
@dataclass
class ESConfig:
    host: str
    port: int
    index_name: str


# LLM配置，对应app_config.yaml中的llm
@dataclass
class LLMConfig:
    mode_name: str
    api_key: str
    base_url: str


# AppConfig 是整个项目的配置类，包含了所有配置项
@dataclass
class AppConfig:
    logging: LoggingConfig
    db_meta: DBConfig
    db_dw: DBConfig
    qdrant: QdrantConfig
    embedding: EmbeddingConfig
    es: ESConfig
    llm: LLMConfig


# 从配置文件加载加载配置
config_file = Path(__file__).parents[2] / "conf" / "app_config.yaml"

load_dotenv()
config = OmegaConf.load(config_file)

# 验证配置是否符合预期
schema = OmegaConf.structured(AppConfig)

# 合并配置
app_config: AppConfig = OmegaConf.to_object(OmegaConf.merge(schema, config))


if __name__ == "__main__":
    # 测试：打印Elasticsearch主机名
    print(app_config.es.host)
