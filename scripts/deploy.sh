#!/bin/sh

CONTAINERS_TO_BUILD="webapp webapp-celery"

git pull

docker compose --env-file .env up -d --build $(CONTAINERS_TO_BUILD)
