FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev --no-cache

COPY app.py ./

CMD ["uv", "run", "--no-sync", "app.py"]
