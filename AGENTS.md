# Agent Guidelines for smllr

## Build & Test Commands
- **Install dependencies**: `uv sync`
- **Run server**: `python manage.py runserver`
- **Watch CSS**: `npm run dev` (separate terminal)
- **Build CSS**: `npm run build`
- **Run all tests**: `python manage.py test`
- **Run single test**: `python manage.py test smllr.shorturls.tests.ShortURLTestCase.test_anon_user_shorturl_limit`
- **Run app tests**: `python manage.py test smllr.shorturls`
- **Migrations**: `python manage.py makemigrations` then `python manage.py migrate`
- **Lint/Format**: `ruff check .` and `ruff format .`

## Code Style
- **Python**: 3.12+, Django 5.2+, type hints required (`str | None`, not `Optional[str]`)
- **Imports**: Group stdlib → Django → third-party → local, use `from` imports for Django (`from django.db import models`)
- **Models**: Use custom managers, type annotate (`objects: CustomManager = CustomManager()`), prefer `models.ForeignKey` with `on_delete`
- **Views**: Class-based views (CBVs), use mixins for auth/subscriptions, transactions with `@transaction.atomic`
- **Naming**: snake_case for functions/variables, PascalCase for classes, descriptive names (`short_code` not `code`)
- **Error handling**: Use logging (`logging.getLogger(__name__)`), catch specific exceptions, use `exc_info=True` for stack traces
- **Strings**: Use `gettext` for user-facing strings: `from django.utils.translation import gettext as _`
