from django.http import JsonResponse
from django.shortcuts import render
from rest_framework.decorators import api_view

from endpoint.models import User, Profile, Article, Tag
from endpoint.serializers import UserSerializer, ProfileSerializer, ArticleSerializer, TagSerializer


# Create your views here.


@api_view(['GET'])
def health_check(request):
    return JsonResponse({"HealthCheck": "OK"})


# def get_current_user(request):
#     if request.method == 'GET':
#         user = User.objects.all()
#         serializer = UserSerializer(user, many=True)
#         return JsonResponse(serializer.data, safe=False)


@api_view(['GET'])
def get_profile(request, username):
    profile = Profile.objects.get(username=username)
    serializer = ProfileSerializer(profile)
    return JsonResponse(serializer.data, safe=False)


@api_view(['GET'])
def get_article(request, slug):
    article = Article.objects.get(slug=slug)
    serializer = ArticleSerializer(article)
    return JsonResponse(serializer.data, safe=False)


@api_view(['GET'])
def get_tags_list(request):
    tags = Tag.objects.all()
    serializer = TagSerializer(tags, many=True)
    return JsonResponse(serializer.data, safe=False)
