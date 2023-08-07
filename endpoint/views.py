from django.http import JsonResponse
from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import AllowAny
from rest_framework import viewsets, exceptions
from rest_framework.views import APIView
from rest_framework.response import Response

# from endpoint.models import User, Profile, Article, Tag
# from endpoint.serializers import UserSerializer, ProfileSerializer, ArticleSerializer, TagSerializer, \
#     AuthenticationSerializer, RegistrationSerializer


# Create your views here.


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    return JsonResponse({"HealthCheck": "OK"}, safe=False)


# class AuthenticationList(APIView):
#     permission_classes = [AllowAny]
#     serializer_class = AuthenticationSerializer
#
#     def post(self, request):
#         # email = request.data['user']['email']
#
#         user = request.data.get('user', {})
#
#         serializer = self.serializer_class(data=user)
#         serializer.is_valid()
#
#         return Response(serializer.data, status=status.HTTP_200_OK)
#
#
# class RegistrationList(APIView):
#     permission_classes = [AllowAny]
#     serializer_class = RegistrationSerializer
#
#     def post(self, request):
#         # username = request.data['user']['username']
#         # email = request.data['user']['email']
#         # password = request.data['user']['password']
#
#         user = request.data.get('user', {})
#
#         serializer = self.serializer_class(data=user)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#
#         return Response(serializer.data, status=status.HTTP_201_CREATED)
#
#
# # def get_current_user(request):
# #     if request.method == 'GET':
# #         user = User.objects.all()
# #         serializer = UserSerializer(user, many=True)
# #         return JsonResponse(serializer.data, safe=False)
#
# class ProfileViewSet(viewsets.ModelViewSet):
#     queryset = Profile.objects.all()
#     serializer_class = ProfileSerializer
#
#     @action(detail=False, methods=['GET'], url_path='(?P<username>\w+)')
#     def by_username(self, request, username):
#         profile = self.get_queryset().get(username=username)
#         serializer = self.get_serializer(profile)
#         return Response(serializer.data)
#
#
# @api_view(['GET'])
# def get_profile(request, username):
#     profile = Profile.objects.get(username=username)
#     serializer = ProfileSerializer(profile)
#     return JsonResponse(serializer.data, safe=False)
#
#
# # Article
# @api_view(['GET'])
# @permission_classes([AllowAny])
# def get_article(request, slug):
#     article = Article.objects.get(slug=slug)
#     serializer = ArticleSerializer(article)
#     return JsonResponse(serializer.data, safe=False)
#
#
# @api_view(['POST'])
# def create_article(request, article):
#     toSave = Article(title=article.title, description=article.description, body=article.body)
#     toSave.save()
#     serializer = ArticleSerializer(toSave)
#     return JsonResponse(serializer.data, safe=False)
#
#
# @api_view(['PUT'])
# def update_article(request, slug, article):
#     toSave = Article.objects.get(slug=slug)
#     toSave.title = article.title
#     toSave.description = article.description
#     toSave.body = article.body
#     toSave.save()
#     serializer = ArticleSerializer(toSave)
#     return JsonResponse(serializer.data, safe=False)
#
#
# @api_view(['DELETE'])
# def delete_article(request, slug):
#     article = Article.objects.get(slug=slug)
#     article.delete()
#     return None
#
#
# # Tag
# @api_view(['GET'])
# @permission_classes([AllowAny])
# def get_tags_list(request):
#     tags = Tag.objects.all()
#     serializer = TagSerializer(tags, many=True)
#     return JsonResponse(serializer.data, safe=False)
