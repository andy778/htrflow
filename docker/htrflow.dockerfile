ARG PYTHON_VERSION=3.10
ARG DEBIAN_FRONTEND=noninteractive

# nvidia/cuda:12.1.0-base-ubuntu22.04
FROM nvidia/cuda@sha256:40042016a816cbbe0504dd0a396e7cfc036a8aa43f5694af60dd6f8f87d24e52 AS builder

ARG PYTHON_VERSION
ARG DEBIAN_FRONTEND

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    python${PYTHON_VERSION} \
    python3-pip \
    python3-dev \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# ghcr.io/astral-sh/uv:latest
COPY --from=ghcr.io/astral-sh/uv@sha256:77280f2f771df71f90786c314fe1bbc1e023feac652969bbf139c280babf2eb7 /uv /bin/

WORKDIR /app

ENV UV_LINK_MODE=copy
ENV UV_COMPILE_BYTECODE=1
ENV UV_NO_CACHE=1

RUN uv venv --python ${PYTHON_VERSION}

# Install dependencies first (for better layer caching)
COPY uv.lock pyproject.toml /app/
RUN uv sync --frozen --no-install-project

COPY src/ /app/src/
COPY LICENSE README.md /app/

# Install project
RUN uv sync --frozen

# nvidia/cuda:12.1.0-base-ubuntu22.04
FROM nvidia/cuda@sha256:40042016a816cbbe0504dd0a396e7cfc036a8aa43f5694af60dd6f8f87d24e52 AS runtime

ARG PYTHON_VERSION
ARG DEBIAN_FRONTEND

RUN apt-get update && apt-get install -y --no-install-recommends \
    python${PYTHON_VERSION} \
    libgl1 \
    libglib2.0-0 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/src /app/src

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app:$PYTHONPATH"