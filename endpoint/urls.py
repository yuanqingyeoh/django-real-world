from django.urls import path, include
from rest_framework.routers import DefaultRouter

from endpoint import views
#
# router = DefaultRouter()
# router.register(r'profiles', ProfileViewSet, basename="profiles")

urlpatterns = [
    # path('', include(router.urls)),
    path('healthcheck/', views.health_check),
    path('users/login', views.user_login),
    path('users', views.user_registration),
    # # path('profiles/<str:username>', ProfileViewSet.as_view({'get': 'by_username'})),
    # # path('profiles/<str:username>', get_profile),
    # path('articles/<str:slug>', get_article),
    # path('tags', get_tags_list)
]