FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml uv.lock .
COPY package.json package-lock.json .

RUN apt-get update && apt-get upgrade -y

COPY --from=ghcr.io/astral-sh/uv:0.9.4 /uv /uvx /bin/

ADD . /app

RUN uv sync --locked

CMD ["uv", "run", "celery", "-A", "smllr", "worker", "-l", "INFO"]
