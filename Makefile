docker_compose_env_file = .env
docker_compose_cmd = docker compose --env-file $(docker_compose_env_file)

up-no-docker:
	$(docker_compose_cmd) --profile dev up -d
	python manage.py runserver

up-dev:
	$(docker_compose_cmd) --profile dev up -d

up:
	$(docker_compose_cmd) --profile prd up -d
