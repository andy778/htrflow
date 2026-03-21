FROM nvidia/cuda:12.9.1-base-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.10 \
    python3-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:0.10.3 /uv /bin/uv

WORKDIR /app

ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

RUN uv venv --python 3.10

# Install dependencies before copying source for better layer caching
COPY uv.lock pyproject.toml /app/
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project

COPY src/ /app/src/
COPY LICENSE README.md /app/

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen

ENV PYTHONPATH="/app:$PYTHONPATH"

ENTRYPOINT ["htrflow"]
CMD ["--help"]
