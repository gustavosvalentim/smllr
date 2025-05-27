FROM python:3.10-slim

WORKDIR /app

COPY pyproject.toml .
COPY uv.lock .

RUN apt-get update -y \
    && apt-get upgrade -y \
    && pip install --upgrade pip \
    && pip install uv \
    && uv sync --frozen --no-install-project --no-dev

ENV PATH="/app/.venv/bin:$PATH"

ADD . /app

EXPOSE 8000

ENTRYPOINT ["sh", "scripts/entrypoint.sh"]