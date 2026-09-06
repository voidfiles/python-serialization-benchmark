FROM ghcr.io/astral-sh/uv:0.12.10 AS uv
FROM python:3.14-slim

COPY --from=uv /uv /uvx /bin/
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

WORKDIR /app
COPY pyproject.toml uv.lock README.md ./
COPY serialization_benchmark ./serialization_benchmark
COPY tests ./tests
RUN uv sync --locked

ENTRYPOINT ["uv", "run", "--locked", "serialization-benchmark"]
CMD ["validate"]
