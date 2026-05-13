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
   PYTHONPATH=. uv run --dev -m gunicorn -c src/gunicorn.py src.app:app
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
docker build -f templates/python/service/Dockerfile --target runtime -t python-template-dev .
```

To run the container locally, mount the port and explicitly set `ENV=development` to disable the forced HTTPS redirects from Talisman:

```bash
docker run -d --rm -p 8018:8018 -e ENV=development --env-file .env --name python-template-dev python-template-dev
```

Before using this outside this monorepo, replace the local `authorization-in-the-middle` source override in `pyproject.toml` with an immutable published artifact.

## Test Matrix

- `tests/unit/` tests pure business logic, helpers, and pure functions without I/O or routing.
- `tests/integration/` exercises the Flask routing, schema validation, and real un-mocked requests. Validates OpenAPI contract and response shapes.
- `tests/integration/test_container.py` runs a real Docker container using `testcontainers` to ensure the built image responds successfully to health queries.
- `tests/benchmark.py` stress tests concurrency, AuthN bottlenecks, and rate limiting natively.

## High-Throughput Benchmarking

You can profile API boundaries via `tests/benchmark.py`. This script spins up concurrent asynchronous clients to hammer the local application endpoint.

When benchmarking container capacity locally via Docker:
1. **Disable the Docker Log Driver**: Docker's default `json-file` log driver will become IO-bound at ~500 RPS as it streams massive amounts of 200 OK logs to your local hard drive. Pass `--log-driver none` to the `docker run` command to bypass this constraint for load testing.
2. **Tune Rate Limits**: By default, `DOCUMENT_READ_RATE_LIMIT` strictly throttles to `60 per minute`. To test real server throughput, inject `-e DOCUMENT_READ_RATE_LIMIT="10000 per second"` to open the floodgates.
3. **Set Workers**: Set `-e WEB_CONCURRENCY=X` matching CPU capacity. For example, `WEB_CONCURRENCY=16` handles 500+ sustained RPS with ~30ms latencies natively.
