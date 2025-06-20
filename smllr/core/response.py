from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def not_found(request: HttpRequest, message: str | None = None) -> HttpResponse:
    return render(request, 'smllr/404.html', {'message': message},  status=404)
