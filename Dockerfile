FROM python:3.13.7-slim

WORKDIR /app

COPY pyproject.toml uv.lock .
COPY package.json package-lock.json .

RUN apt-get update -y \
    && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends curl build-essential gcc python3-dev libssl-dev \
    && pip install --upgrade pip \
    && pip install uv \
    && uv sync --frozen --no-install-project --no-dev 

COPY . . 

# Download and install nvm:
SHELL ["/bin/bash", "-c"]
RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash 
RUN source $HOME/.nvm/nvm.sh \
    && nvm install --lts \
    && npm install \
    && npm run build 

# Set python deps on PATH
ENV PATH="/app/.venv/bin:$PATH"

# Handle django static files
RUN python manage.py collectstatic --noinput

EXPOSE 8000

ENTRYPOINT ["/bin/sh", "/app/scripts/entrypoint.sh"]

