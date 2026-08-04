# huggingface/transformers-pytorch-gpu:4.41.2
FROM huggingface/transformers-pytorch-gpu@sha256:4c7317881a534b22e18add49c925096fa902651fb0571c69f3cad58af3ea2c0f
# ghcr.io/astral-sh/uv:latest
COPY --from=ghcr.io/astral-sh/uv@sha256:77280f2f771df71f90786c314fe1bbc1e023feac652969bbf139c280babf2eb7 /uv /bin/


WORKDIR /app

RUN uv venv --python 3.10.14


ADD uv.lock /app/uv.lock
ADD pyproject.toml /app/pyproject.toml
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project

COPY src LICENSE README.md examples /app/

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen 

RUN uv pip install -U https://github.com/Swedish-National-Archives-AI-lab/openmim_install/raw/main/mmcv-2.0.0-cp310-cp310-manylinux1_x86_64.whl && \
    uv pip install -U mmdet==3.1.0 mmengine==0.7.2 mmocr==1.0.1 yapf==0.40.1

ENV PATH="/app/.venv/bin:$PATH"