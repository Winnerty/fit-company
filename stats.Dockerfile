FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1

ENV UV_LINK_MODE=copy

COPY pyproject.toml uv.lock ./

RUN uv sync

COPY main_stats.py /app/main_stats.py

ENV FLASK_ENV=development

EXPOSE 5000

CMD ["uv", "run", "main_stats.py"] 