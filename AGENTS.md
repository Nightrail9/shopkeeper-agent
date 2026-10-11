# Repository Guidelines

## Project Overview

`shopkeeper-agent` is a Python project scaffold. The business purpose is not documented yet; the current application entry point only prints a greeting. Do not treat declared dependencies or directory names as implemented features.

## Architecture & Data Flow

The declared command maps `shopkeeper-agent` to `app.main` (`pyproject.toml`). Its only current flow is `app.main()` printing `Hello from shopkeeper-agent!`. The `app/` subpackages are empty placeholders; there is no implemented API, agent graph, persistence layer, configuration loading, or business data flow to extend by imitation.

## Key Directories

- `app/agent/`, `app/api/`, `app/clients/`, `app/core/`, `app/entities/`, `app/models/`, `app/prompt/`, `app/repositories/`, `app/services/`: empty Python package placeholders; preserve these boundaries when implementing corresponding concerns.
- `app/scripts/`: placeholder for project scripts; none exist yet.
- `conf/`, `prompts/`: empty project-level resource directories.
- `docker/embedding/bge-large-zh-v1.5/`: model/tokenizer files are present locally; `pytorch_model.bin` is ignored because of its size. No application code currently loads the model.
- `docker/elasticsearch/`, `docker/mysql/`: empty placeholders; no Docker or service startup configuration is present.
- `logs/`: empty runtime-output directory.

## Development Commands

- Install/sync locked dependencies: `uv sync`.
- Build the package: `uv build`.
- Run the declared console entry point after syncing: `uv run shopkeeper-agent`.
- Direct smoke run: `python -c "from app import main; main()"`.

`uv build` and the direct smoke run have been verified. `pyproject.toml` declares `uv_build` as the build backend and configures the root-level `app` package.

## Code Conventions & Common Patterns

There is no established application-level pattern yet: the only non-empty Python file is `app/__init__.py`, whose `main()` has a `-> None` return annotation. Use standard Python naming (`snake_case` for functions/modules, `PascalCase` for classes), keep changes within the corresponding `app/` package, and add type annotations to public interfaces. No repository precedent exists yet for error handling, async I/O, dependency injection, or agent state management; avoid claiming or introducing a framework pattern without a concrete requirement.

## Important Files

- `pyproject.toml`: project metadata, dependencies, `shopkeeper-agent` entry point, and `uv_build` configuration.
- `uv.lock`: locked dependency graph; use with `uv` rather than editing resolved versions by hand.
- `.python-version`: pins Python `3.14`; `pyproject.toml` requires `>=3.14`.
- `app/__init__.py`: current `main()` entry point.
- `docker/embedding/bge-large-zh-v1.5/README.md`: upstream model documentation, not project setup instructions.
- `README.md`: currently empty; no project-specific setup or runtime configuration is documented.

## Runtime/Tooling Preferences

Use Python 3.14+ and `uv`; dependencies are declared in `pyproject.toml` and locked in `uv.lock`. The project has no configured Node/Bun toolchain. Although dependencies include FastAPI, LangChain/LangGraph, database and vector/search clients, their presence in metadata does not mean those services are implemented or configured.

## Testing & QA

No `tests/` or `test/` directory, test framework configuration, CI workflow, lint configuration, formatter, or type checker is currently present. Do not report a test/lint command as project-defined. For changes to the current entry point, the direct smoke command above exercises its behavior; add focused tests when implementing testable application behavior and document the chosen test command then.
