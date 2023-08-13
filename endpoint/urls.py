from django.urls import path, include
from rest_framework.routers import SimpleRouter
from endpoint import views

router = SimpleRouter(trailing_slash=False)
router.register(r'articles', views.ArticleViewSet)

router2 = SimpleRouter(trailing_slash=False)
router2.register(r'comments', views.CommentViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('healthcheck', views.health_check),
    path('users/login', views.user_login),
    path('users', views.user_registration),
    path('user', views.UserView.as_view()),
    path('profiles/<str:username>', views.ProfileView.as_view()),
    path('profiles/<str:username>/follow', views.ProfileView.as_view()),
    path('articles/<slug:article_slug>/', include(router2.urls)),
    path('tags', views.get_tags_list)
]