from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import viewsets, exceptions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from endpoint.models import User, Article, Comment, Tag

from endpoint.serializers import UserSerializer, ProfileSerializer, ArticleSerializer, TagSerializer


# from endpoint.models import User, Profile, Article, Tag
# from endpoint.serializers import UserSerializer, ProfileSerializer, ArticleSerializer, TagSerializer, \
#     AuthenticationSerializer, RegistrationSerializer


# Create your views here.


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    return JsonResponse({"HealthCheck": "OK"}, safe=False)


@api_view(['POST'])
@permission_classes([AllowAny])
def user_registration(request):
    try:
        user_data = request.data.get('user')
        serializer = UserSerializer(data=user_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'user': serializer.data}, status=status.HTTP_201_CREATED)

    except exceptions.ValidationError as validation_error:
        return Response({'error': validation_error.detail}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as generic_error:
        return Response({'error': 'An error occurred during user registration.'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def user_login(request):
    try:
        user_data = request.data.get('user')
        user = authenticate(email=user_data['email'],  password=user_data['password'])
        serializer = UserSerializer(user)
        jwt_token = RefreshToken.for_user(user)
        serializer_data = serializer.data
        serializer_data['token'] = str(jwt_token.access_token)
        response_data = {
            'user': serializer_data
        }
        return Response(response_data, status=status.HTTP_202_ACCEPTED)

    except Exception:
        return Response(status=status.HTTP_400_BAD_REQUEST)


class UserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):

        request_user = request.user

        serializer = ProfileSerializer(request_user, context={'request': request})

        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, format=None):
        request_user = request.user
        user_data = request.data.get('user')
        user = User.objects.filter(pk=request_user.id).get()

        serializer = ProfileSerializer(user, data=user_data, partial=True, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


class ProfileView(APIView):
    permission_classes_by_method = {
        'GET': [AllowAny()],
        'POST': [IsAuthenticated()],
        'DELETE': [IsAuthenticated()],
    }

    def get(self, request, username, format=None):

        user = User.objects.filter(username=username).get()

        serializer = ProfileSerializer(user, context={'request': request})

        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, username, format=None):
        request_user = request.user
        follower = User.objects.filter(pk=request_user.id).get()
        toFollow = User.objects.filter(username=username).get()
        if follower == toFollow:
            return Response({
                'errors': {
                    'body': [
                        'Invalid Follow Request'
                    ]
                }
            }, status=status.HTTP_400_BAD_REQUEST)

        toFollow.followers.add(follower)
        serializer = ProfileSerializer(toFollow, data={'follower': toFollow.followers}, partial=True, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, username, format=None):
        request_user = request.user
        toUnfollow = User.objects.get(username=username)
        toUnfollow.followers.remove(request_user)

        serializer = ProfileSerializer(toUnfollow, data={'follower': toUnfollow.followers}, partial=True, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    lookup_field = 'slug'
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action == 'retrieve':
            return [AllowAny()]
        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        article_data = request.data.get('article')

        # Handle Tag
        tag_list = []
        for tag_str in article_data.get('tagList'):
            obj, created = Tag.objects.get_or_create(tag=tag_str)
            tag_list.append(obj)

        article_data['tagList'] = tag_list
        serializer = self.get_serializer(data=article_data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def retrieve(self, request, slug, *args, **kwargs):
        article = self.get_queryset().get(slug=slug)
        serializer = self.get_serializer(article, context={'request': request})

        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, slug, *args, **kwargs):
        article_data = request.data.get('article')
        article = self.get_queryset().get(slug=slug)

        serializer = self.get_serializer(article, data=article_data, partial=True, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, slug, *args, **kwargs):
        article = self.get_queryset().get(slug=slug)
        if article.author != request.user:
            return Response({'error' : {
                'body': ['Unauthorised action']
            }}, status=status.HTTP_401_UNAUTHORIZED)
        article.delete()

        return Response(status=status.HTTP_200_OK)


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

# Tag
@api_view(['GET'])
@permission_classes([AllowAny])
def get_tags_list(request):
    tags = Tag.objects.all()
    serializer = TagSerializer(tags, many=True)

    output = [tag['tag'] for tag in serializer.data]
    return JsonResponse({'tags':  output}, safe=False)
