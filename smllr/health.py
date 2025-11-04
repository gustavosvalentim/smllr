from django.views import View
from django.http import HttpRequest, JsonResponse


class HealthCheckView(View):
    def get(self, request: HttpRequest):
        return JsonResponse({"status": "Ok"})
