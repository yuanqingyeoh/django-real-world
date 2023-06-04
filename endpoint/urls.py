from django.urls import path

from endpoint.views import health_check

urlpatterns = [
    path('healthcheck/', health_check)
]