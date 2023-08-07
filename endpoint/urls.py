from django.urls import path, include
from rest_framework.routers import DefaultRouter

from endpoint.views import health_check\
    # , get_profile, get_article, create_article, get_tags_list, ProfileViewSet, \
    # AuthenticationList, RegistrationList
#
# router = DefaultRouter()
# router.register(r'profiles', ProfileViewSet, basename="profiles")

urlpatterns = [
    # path('', include(router.urls)),
    path('healthcheck/', health_check),
    # path('users/login', AuthenticationList.as_view()),
    # path('users', RegistrationList.as_view()),
    # # path('profiles/<str:username>', ProfileViewSet.as_view({'get': 'by_username'})),
    # # path('profiles/<str:username>', get_profile),
    # path('articles/<str:slug>', get_article),
    # path('tags', get_tags_list)
]