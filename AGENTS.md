# Repository Guidelines

## Project Overview

`shopkeeper-agent` implements an e-commerce natural-language analytics service: users ask questions, the backend retrieves business metadata, generates and checks MySQL SQL, runs it against the warehouse, and streams progress/results to a React frontend. The runtime depends on MySQL, Elasticsearch, Qdrant, an OpenAI-compatible embedding service, and an LLM API.

## Architecture & Data Flow

- HTTP entry point: `main.py` creates the FastAPI app, installs request-ID middleware and lifespan, and binds Uvicorn to `127.0.0.1:8000`. The `shopkeeper-agent` console script invokes `main:run`; `app/__init__.py::main` only prints a greeting and is not the API launcher.
- Query flow: `POST /api/query` → `QueryService` → LangGraph nodes → metadata/value retrieval and LLM SQL generation → `EXPLAIN` validation (one correction attempt) → DW MySQL execution → SSE progress/result/error events. Frontend step labels in `frontend/src/components/StepRail.tsx` must exactly match backend node `step` strings.
- Metadata indexing: `app/scripts/build_meta_knowledge.py` loads `conf/meta_config.yaml`, reads warehouse metadata and values, and writes relational metadata plus Qdrant vectors and Elasticsearch values. This rebuild deletes/recreates affected records, collections, and index; it is not read-only or incremental.
- Layers: API routes/schemas/dependencies, services, LangGraph agent/nodes, client managers, and repositories. Services receive repositories/clients through constructors; FastAPI dependencies assemble request-scoped services. There is no general-purpose DI container.
- SQL `EXPLAIN` is not a read-only SQL allowlist or security boundary. The query API has no authentication; keep the backend bound to loopback unless access controls are added.

## Key Directories

- `app/api/`: FastAPI routes, Pydantic schemas, dependencies, and client lifespan.
- `app/agent/`: LangGraph state, runtime context, graph, and nodes.
- `app/services/`: query/SSE orchestration and metadata knowledge construction.
- `app/repositories/`: MySQL, Qdrant, and Elasticsearch persistence and retrieval.
- `app/clients/`: async database/search/vector clients and embedding HTTP clients.
- `app/conf/`, `conf/`: typed configuration loaders/schemas and YAML settings.
- `app/models/`, `app/entities/`: SQLAlchemy ORM models and dataclass business entities.
- `prompts/`: prompt templates loaded by `app/prompt/prompt_loader.py`.
- `frontend/src/`: React UI and API/SSE types; `docker/`: local service definitions and MySQL initialization assets.

## Development Commands

Run from the repository root unless noted:

```bash
uv sync
uv build
uv run shopkeeper-agent
docker compose -f docker/docker-compose.yaml config
docker compose -f docker/docker-compose.yaml up -d
docker compose -f docker/docker-compose.yaml down
```

The backend command starts on `127.0.0.1:8000`. MySQL initialization scripts run only for an empty data directory; `down -v` permanently deletes persisted local data and should not be used casually. Download missing embedding model files with:

```bash
uv run hf download BAAI/bge-large-zh-v1.5 --local-dir docker/embedding/bge-large-zh-v1.5
```

Frontend commands run in `frontend/`:

```bash
pnpm install
pnpm dev       # Vite on :5173; /api proxies to the backend
pnpm lint      # TypeScript check, not ESLint
pnpm build     # TypeScript check + production build
```

Build metadata with `uv run python -m app.scripts.build_meta_knowledge --config_path conf/meta_config.yaml`; this modifies/deletes external service data. Review script side effects before running any client or example `__main__` demo.

## Code Conventions & Common Patterns

- Follow existing Python naming: `snake_case` for modules/functions/variables, `PascalCase` for classes; use `app.*` absolute imports. Add annotations to public interfaces and follow neighboring docstring/comment style.
- Extend structured dataclasses and OmegaConf configuration rather than reading YAML ad hoc. Secrets come from `.env` interpolation; never commit secret values.
- Client managers are module-level singletons with explicit `init()`/`close()` lifecycle. Initialize/close them through `app/api/lifespan.py`; close async clients in `finally` or lifespan cleanup.
- Keep request-scoped SQLAlchemy sessions in FastAPI dependencies. Repositories use the injected session; service-level `session.begin()` owns transaction boundaries.
- LangGraph nodes take `(state, runtime)`, read shared dependencies from `runtime.context`, and return partial state updates. Emit progress using the existing stream event shape and preserve the current SSE one-line JSON framing (`data: ...\n\n`).
- Use `app.core.log.logger` for application logs and the existing request-ID `ContextVar` integration. LLM prompts live in `prompts/`; compose chains using neighboring LangChain prompt/parser patterns.

## Important Files

- `main.py`: Uvicorn/FastAPI launcher.
- `app/api/routers/query_router.py`, `app/services/query_service.py`: query endpoint and SSE orchestration.
- `app/agent/graph.py`, `app/agent/nodes/`, `app/agent/state.py`: query graph and shared state.
- `app/services/meta_knowledge_service.py`, `app/scripts/build_meta_knowledge.py`: metadata indexing workflow and CLI.
- `app/conf/app_config.py`, `app/conf/meta_config.py`, `conf/app_config.yaml`, `conf/meta_config.yaml`: configuration schemas and values.
- `pyproject.toml`, `uv.lock`, `.python-version`: Python package, locked dependencies, and runtime version.
- `docker/docker-compose.yaml`, `README.md`, `frontend/README.md`: local infrastructure and run instructions.

## Runtime/Tooling Preferences

- Python `>=3.14`; use `uv` for Python environments, dependencies, and builds. Do not hand-edit `uv.lock`; Elasticsearch dependency is constrained to `>=8,<9`.
- Frontend uses pnpm (`pnpm@10.33.0`) with React 19, TypeScript, and Vite. Use `pnpm` in `frontend/`; no repository Node version pin exists.
- The Embedding container targets `linux/amd64` and reads local model assets; weights are excluded from Git. Local `.env` files contain secrets and are ignored.

## Testing & QA

- No automated backend/frontend test suite, coverage target, or Python lint/typecheck command is configured. Do not report manual service demos as tests.
- `pnpm lint` performs TypeScript checking; `pnpm build` checks types and builds the UI. Both run from `frontend/`.
- Client `__main__` blocks and examples are service-touching manual demos; some create, upsert, or delete data. The metadata build is destructive. Inspect effects and use disposable data before running them.
- End-to-end query/SSE checks require the backend, configured `.env`, and external services. Frontend dev proxy defaults to `http://127.0.0.1:8000`; the contract is `POST /api/query` with JSON `{"query":"..."}` and `text/event-stream` responses.
