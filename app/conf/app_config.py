from dataclasses import field
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv
from omegaconf import OmegaConf
import omegaconf


# 文件日志配置，对应app_config.yaml中的logging.file
@dataclass
class File:
    enable: bool = True
    level: str = "INFO"
    path: str = "logs"
    rotation: str = "10 MB"
    retention: str = "7 days"


# 控制台日志配置，对应app_config.yaml中的logging.console
@dataclass
class Console:
    enable: bool = True
    level: str = "INFO"


# 日志配置
@dataclass
class LoggingConfig:
    file: File = field(default_factory=File)
    console: Console = field(default_factory=Console)


# 数据库配置
@dataclass
class DBConfig:
    host: str = "localhost"
    port: int = 3306
    user: str = "bob"
    password: str = "bob123"
    database: str = "meta"


# Qdrant配置，对应app_config.yaml中的qdrant
@dataclass
class QdrantConfig:
    host: str = "localhost"
    port: int = 6333
    embedding_dim: int = 1024


# 嵌入模型配置，对应app_config.yaml中的embedding
@dataclass
class EmbeddingConfig:
    host: str = "localhost"
    port: int = 8081
    model: str = "BAAI/bge-large-zh-v1.5"


# Elasticsearch配置，对应app_config.yaml中的elasticsearch
@dataclass
class ESConfig:
    host: str = "localhost"
    port: int = 9200
    index_name: str = "data_agent"


# LLM配置，对应app_config.yaml中的llm
@dataclass
class LLMConfig:
    mode_name: str = "deepseek-ai/DeepSeek-V4.1-Flash"
    api_key: str = ""
    base_url: str = "https://api-inference.modelscope.cn/v1"


# AppConfig 是整个项目的配置类，包含了所有配置项
@dataclass
class AppConfig:
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    db_meta: DBConfig = field(default_factory=DBConfig)
    db_dw: DBConfig = field(default_factory=DBConfig)
    qdrant: QdrantConfig = field(default_factory=QdrantConfig)
    embedding: EmbeddingConfig = field(default_factory=EmbeddingConfig)
    es: ESConfig = field(default_factory=ESConfig)
    llm: LLMConfig = field(default_factory=LLMConfig)


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
