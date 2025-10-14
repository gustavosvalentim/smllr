FROM python:3.13.7-slim

WORKDIR /app

COPY pyproject.toml .
COPY uv.lock .

RUN apt-get update -y \
    && apt-get upgrade -y \
    && pip install --upgrade pip \
    && pip install uv \
    && uv sync --frozen --no-install-project --no-dev

# Download and install nvm:
RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash \
    source "$HOME/.nvm/nvm.sh" \
    nvm install 22

# Build static files such as CSS
RUN npm run build

# Handle django static files
RUN python manage.py collectstatic --noinput

ENV PATH="/app/.venv/bin:$PATH"

ADD . /app

EXPOSE 8000

ENTRYPOINT ["sh", "scripts/entrypoint.sh"]
