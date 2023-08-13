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
from django.core import exceptions as e

from endpoint.serializers import UserSerializer, ProfileSerializer, ArticleSerializer, TagSerializer, CommentSerializer



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
        return Response({'article': serializer.data}, status=status.HTTP_201_CREATED, headers=headers)

    def retrieve(self, request, slug, *args, **kwargs):
        article = self.get_queryset().get(slug=slug)
        serializer = self.get_serializer(article, context={'request': request})

        return Response({'article': serializer.data}, status=status.HTTP_200_OK)

    def update(self, request, slug, *args, **kwargs):
        article_data = request.data.get('article')
        article = self.get_queryset().get(slug=slug)

        serializer = self.get_serializer(article, data=article_data, partial=True, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'article': serializer.data}, status=status.HTTP_200_OK)

    def destroy(self, request, slug, *args, **kwargs):
        article = self.get_queryset().get(slug=slug)
        if article.author != request.user:
            return Response({'error' : {
                'body': ['Unauthorised action']
            }}, status=status.HTTP_401_UNAUTHORIZED)
        article.delete()

        return Response(status=status.HTTP_200_OK)

    @action(detail=True, methods=['post', 'delete'])
    def favorite(self, request, slug, *args, **kwargs):
        if request.method == 'POST':
            article = self.get_queryset().get(slug=slug)
            existed = article.favorites.filter(pk=request.user.id).exists()
            if not existed:
                article.favorites.add(request.user)

            serializer = self.get_serializer(article, data={'favorites': article.favorites}, partial=True, context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response({'article': serializer.data}, status=status.HTTP_200_OK)

        elif request.method == 'DELETE':
            article = self.get_queryset().get(slug=slug)
            existed = article.favorites.filter(pk=request.user.id).exists()
            if existed:
                article.favorites.remove(request.user)

            serializer = self.get_serializer(article, data={'favorites': article.favorites}, partial=True,
                                             context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response({'article': serializer.data}, status=status.HTTP_200_OK)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action == 'list':
            return [AllowAny()]
        return super().get_permissions()

    def list(self, request, article_slug, *args, **kwargs):
        try:
            article = Article.objects.get(slug=article_slug)
            comments = list(self.get_queryset().filter(article=article))

            serializer = self.get_serializer(comments, many=True, context={'request': request})

            return Response({'comments': serializer.data}, status=status.HTTP_200_OK)
        except e.ObjectDoesNotExist:
            return Response({'error': 'Article Does Not Exist'}, status=status.HTTP_400_BAD_REQUEST)


    def create(self, request, article_slug, *args, **kwargs):
        try:
            comment_data = request.data.get('comment')

            article = Article.objects.get(slug=article_slug)

            serializer = self.get_serializer(data=comment_data, context={'request': request, 'article': article})
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response({'comment': serializer.data}, status=status.HTTP_201_CREATED)

        except e.ObjectDoesNotExist:
            return Response({'error': 'Article Does Not Exist'}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, article_slug, *args, **kwargs):
        try:
            article = Article.objects.get(slug=article_slug)
            comment = self.get_queryset().get(article=article, pk=kwargs['pk'])
            if comment.author != request.user:
                return Response({'error' : {
                    'body': ['Unauthorised action']
                }}, status=status.HTTP_401_UNAUTHORIZED)

            comment.delete()

            return Response(status=status.HTTP_200_OK)
        except e.ObjectDoesNotExist:
            return Response({'error': 'Article Does Not Exist'}, status=status.HTTP_400_BAD_REQUEST)


# Tag
@api_view(['GET'])
@permission_classes([AllowAny])
def get_tags_list(request):
    tags = Tag.objects.all()
    serializer = TagSerializer(tags, many=True)

    output = [tag['tag'] for tag in serializer.data]
    return JsonResponse({'tags':  output}, safe=False)
