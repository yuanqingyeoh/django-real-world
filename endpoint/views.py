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
from endpoint.models import User

from endpoint.serializers import UserSerializer, ProfileSerializer


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
# # Tag
# @api_view(['GET'])
# @permission_classes([AllowAny])
# def get_tags_list(request):
#     tags = Tag.objects.all()
#     serializer = TagSerializer(tags, many=True)
#     return JsonResponse(serializer.data, safe=False)
