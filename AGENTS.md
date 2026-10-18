# Repository Guidelines

## Project Overview

`shopkeeper-agent` is an early-stage Python service scaffold targeting a FastAPI + LangChain/LangGraph agent with MySQL, Elasticsearch, and Qdrant backends. Only configuration loading, async ES/Qdrant client managers, and one ES index mapping are implemented so far; the console entry point still prints a greeting. Do not treat declared dependencies or package names as implemented features — most `app/` subpackages are empty.

## Architecture & Data Flow

The actual runtime flow today:

1. `app/conf/app_config.py` loads `.env` (via `python-dotenv`), reads `conf/app_config.yaml`, merges it with `OmegaConf.structured(AppConfig)` defaults, and exports a module-level `app_config` singleton. `AppConfig` composes dataclasses: `LoggingConfig`, `DBConfig`, `QdrantConfig`, `EmbeddingConfig`, `ESConfig`, `LLMConfig` (LLM key resolved from `${oc.env:LLM_API_KEY,''}`).
2. `app/clients/es_client_manager.py` and `app/clients/qdrant_client_manager.py` each define a manager class taking its config dataclass and a module-level singleton (`es_client_manager`, `qdrant_client_manager`) built from `app_config`. Managers hold an optional async SDK client (`AsyncElasticsearch` / `AsyncQdrantClient`), with `init()` to construct it and `close()` to shut it down.
3. `app/repositories/es/value_es_repository.py` currently contains only an `index_mappings` constant (`dynamic=False`, `value` field using `ik_max_word` analyzer); no repository classes exist yet.
4. `app/__init__.py::main()` is the console entry point and only prints `Hello from shopkeeper-agent!`.

Both client manager modules include `if __name__ == "__main__"` demos that exercise the real services (index/upsert/search against local Docker instances) — useful as usage examples.

## Key Directories

- `app/conf/`: configuration dataclasses and loader (`app_config.py`).
- `app/clients/`: external service client managers (Elasticsearch, Qdrant).
- `app/repositories/`: persistence layer; only `es/value_es_repository.py` mapping so far.
- `app/agent/`, `app/api/`, `app/core/`, `app/entities/`, `app/models/`, `app/prompt/`, `app/services/`, `app/scripts/`: empty packages (zero-byte `__init__.py`); keep new code inside the matching boundary.
- `conf/`: runtime config `app_config.yaml` (logging → `logs/`, MySQL :3306, Qdrant :6333, embedding :8081, Elasticsearch :9200, LLM).
- `docker/`: `docker-compose.yaml` (mysql, elasticsearch, kibana, qdrant, embedding), `mysql/{meta.sql,dw.sql}` init scripts (run only on empty data dir), `elasticsearch/Dockerfile` + `plugins/elasticsearch-analysis-ik-8.19.10.zip`, `embedding/bge-large-zh-v1.5/` local model assets.
- `prompts/`, `logs/`: placeholders (`.gitkeep` only).

## Development Commands

```bash
uv sync                  # install locked deps (creates .venv with Python 3.14)
uv build                 # build package (uv_build backend)
uv run shopkeeper-agent  # console entry point -> prints greeting
python -c "from app import main; main()"  # direct smoke run (verified)
```

Local services (from `README.md`, in Chinese):

```bash
docker compose -f docker/docker-compose.yaml config   # validate
docker compose -f docker/docker-compose.yaml up -d    # start mysql/es/kibana/qdrant/embedding
docker compose -f docker/docker-compose.yaml down     # stop, keep data volumes
uv run hf download BAAI/bge-large-zh-v1.5 --local-dir docker/embedding/bge-large-zh-v1.5  # model weights if missing
```

Copy `.env.example` to `.env` and set `LLM_API_KEY`; `.env` is gitignored.

## Code Conventions & Common Patterns

- Naming: `snake_case` functions/variables/module instances, `PascalCase` classes. Existing constant (`index_mappings`) is lowercase — follow surrounding style rather than imposing `UPPER_SNAKE_CASE`.
- Configuration pattern: structured OmegaConf dataclasses with inline defaults, merged over `conf/app_config.yaml`; env secrets via `${oc.env:...}` interpolation. Extend `AppConfig` dataclasses rather than reading YAML ad hoc.
- Client pattern: manager class constructed with its config dataclass, optional async client field, `init()`/`close()` lifecycle, module-level singleton from `app_config`. No DI framework.
- Async: `asyncio`-based SDK clients (`elasticsearch[async]`, `qdrant-client` async), demos driven by `asyncio.run`. ES demo uses `try/finally` to guarantee `close()` — replicate that when adding service-touching code.
- Type annotations: present on public entry points and client fields but inconsistent on internal methods; add annotations to new public interfaces.
- No module docstrings or `__all__` anywhere; package `__init__.py` files stay empty.

## Important Files

- `pyproject.toml`: metadata, dependencies, `shopkeeper-agent = "app:main"` script, `uv_build` backend.
- `uv.lock`: locked dependency graph (requires Python >=3.14); never hand-edit resolved versions.
- `.python-version`: pins Python `3.14`.
- `conf/app_config.yaml`: single source of runtime service configuration.
- `.env.example`: `LLM_API_KEY` template.
- `docker/docker-compose.yaml`: local service topology and ports.
- `app/conf/app_config.py`, `app/clients/es_client_manager.py`, `app/clients/qdrant_client_manager.py`, `app/repositories/es/value_es_repository.py`: the only implemented modules.
- `README.md`: Chinese local-setup guide (Docker services, MySQL init caveat, model download, `.env`).
- `docker/embedding/bge-large-zh-v1.5/README.md`: upstream FlagEmbedding docs, not project setup. `pytorch_model.bin` is gitignored (large weights).

## Runtime/Tooling Preferences

- Python `>=3.14` (pinned in `.python-version` and `uv.lock`); `uv` manages the interpreter and venv. A system Python 3.13 can run the trivial smoke import but is not the project runtime.
- Package manager: `uv` only; there is no Node/Bun toolchain.
- Declared stack (mostly not yet wired): FastAPI, LangChain + LangGraph + langchain-deepseek/huggingface, SQLAlchemy 2 + asyncmy, elasticsearch[async], qdrant-client, loguru, omegaconf, jieba. Their presence in metadata does not mean services are implemented or configured in code.
- Dev dependency group contains only `ipykernel`.

## Testing & QA

- No `tests/` directory, test framework, coverage config, lint/format/typecheck config, pre-commit, or CI workflow exists. Do not cite a test or lint command as project-defined.
- Verification today: run the entry point (`uv run shopkeeper-agent`) or the direct smoke command above; for service-touching modules, run the module's `__main__` demo against the Docker Compose stack.
- When adding testable behavior, introduce a focused test setup and document the command here.
