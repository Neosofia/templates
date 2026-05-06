# Reference multi-stage Dockerfile for the Python service template.
# Build this from the service directory:
#   docker build --target test .
#   docker build --target runtime -t service-template:test .

# cedarpy 4.8.1 needs the glibc manylinux wheel for attribute-based policy evaluation.
ARG PYTHON_IMAGE=python:3.14-slim@sha256:5b3879b6f3cb77e712644d50262d05a7c146b7312d784a18eff7ff5462e77033

FROM ${PYTHON_IMAGE} AS build-base

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends git \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir uv

COPY pyproject.toml ./pyproject.toml
COPY uv.lock ./uv.lock

FROM build-base AS prod-deps
RUN uv sync --frozen --no-dev --no-editable --no-install-project

FROM build-base AS test-deps
RUN uv sync --frozen --all-groups --no-editable --no-install-project

FROM test-deps AS test

COPY src ./src
COPY tests ./tests
COPY policies ./policies
COPY openapi.json ./openapi.json

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH="/app/src"

RUN python -m pytest -q --ignore=tests/integration

FROM ${PYTHON_IMAGE} AS runtime

RUN groupadd --system app \
    && useradd --system --gid app --create-home --home-dir /home/app app

WORKDIR /app

COPY --from=prod-deps /app/.venv /app/.venv

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH="/app/src"

COPY src ./src
COPY policies ./policies
COPY openapi.json ./openapi.json
COPY gunicorn_conf.py ./gunicorn_conf.py
COPY .env.example ./.env.example

EXPOSE 8018

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8018/health', timeout=3).raise_for_status()" || exit 1

USER app

CMD ["python", "-m", "gunicorn", "-c", "gunicorn_conf.py", "main:app"]
