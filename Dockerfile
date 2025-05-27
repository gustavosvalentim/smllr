FROM python:3.10-alpine

WORKDIR /app

COPY pyproject.toml .
COPY uv.lock .

RUN apk add --no-cache gcc musl-dev libffi-dev linux-headers \
    && pip install --upgrade pip \
    && pip install uv \
    && uv sync --locked


ENV PATH="/app/.venv/bin:$PATH"

ADD . /app

ENTRYPOINT 'scripts/entrypoint.sh'