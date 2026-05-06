# Operations

## Local Development

1. Sync dependencies:

   ```bash
   uv sync
   ```

2. Run the test suite:

   ```bash
   uv run --dev -m pytest -q
   ```

3. Start the service locally:

   ```bash
   uv run --dev -m gunicorn -c gunicorn_conf.py main:app
   ```

4. Check health:

   ```bash
   curl http://localhost:8018/health
   ```

## Docker Build

In this monorepo, build from the repository root:

```bash
docker build -f templates/python/service/Dockerfile -t service-template:test .
```

Before using it outside this monorepo, replace the local `authorization-in-the-middle` source override in `pyproject.toml` with an immutable published artifact.

## Test Matrix

- `tests/test_main.py` exercises the service routes and runtime protections.
- `tests/contract/` validates the OpenAPI contract and response shapes.
- `tests/integration/` is reserved for real container tests and is skipped by default.
