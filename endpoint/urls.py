from django.urls import path

from endpoint.views import health_check, get_profile, get_article, get_tags_list

urlpatterns = [
    path('healthcheck/', health_check),
    path('profiles/<str:username>', get_profile),
    path('articles/<str:slug>', get_article),
    path('tags', get_tags_list)
]