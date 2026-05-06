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
   PYTHONPATH=src uv run --dev -m gunicorn -c gunicorn_conf.py main:app
   ```

4. Check health:

   ```bash
   curl http://localhost:8018/health
   ```

5. Generate a local JWT to test secure API endpoints:

   You will need a valid RS256 token matching the local application's keys to access protected endpoints. Run our utility script to generate an RSA Keypair and Token automatically:
   
   ```bash
   uv run scripts/gen_dev_jwt.py --type Patient --sub p1
   ```
   
   The script will output the exact `JWT_PUBLIC_KEY` variable you need to place in your `.env` to start the server properly, along with the Bearer token for your HTTP requests.

## Docker Build & Run

In this monorepo, build from the repository root:

```bash
docker build -f templates/python/service/Dockerfile --target runtime -t service-template-dev .
```

To run the container locally, mount the port and explicitly set `ENV=development` to disable the forced HTTPS redirects from Talisman:

```bash
docker run -d --rm -p 8018:8018 -e ENV=development --env-file .env --name templates-service-dev service-template-dev
```

Before using this outside this monorepo, replace the local `authorization-in-the-middle` source override in `pyproject.toml` with an immutable published artifact.

## Test Matrix

- `tests/test_main.py` exercises the service routes and runtime protections.
- `tests/contract/` validates the OpenAPI contract and response shapes.
- `tests/integration/` is reserved for real container tests and is skipped by default.
