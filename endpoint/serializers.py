from rest_framework import serializers
from endpoint.models import User, Article, Comment, Tag
# from endpoint.models import User, Profile, Article, Tag
from django.contrib.auth import authenticate


# class RegistrationSerializer(serializers.ModelSerializer):
#
#     password = serializers.CharField(
#         max_length=128,
#         min_length=8,
#         write_only=True)
#
#     token = serializers.CharField(max_length=255, read_only=True)
#
#     class Meta:
#         model = User
#         fields = ['email', 'token', 'username', 'password']
#
#     def create(self, validated_data):
#         return User.objects.create_user(**validated_data)
#
#
# class AuthenticationSerializer(serializers.Serializer):
#     email = serializers.CharField(max_length=255)
#     username = serializers.CharField(max_length=255, read_only=True)
#     password = serializers.CharField(max_length=128, write_only=True)
#     token = serializers.CharField(max_length=255, read_only=True)
#
#     def validate(self, data):
#         email = data.get('email', None)
#         password = data.get('password', None)
#
#         if email is None:
#             raise serializers.ValidationError(
#                 'An email address is required for log in.'
#             )
#
#         if password is None:
#             raise serializers.ValidationError(
#                 'A password is required for log in.'
#             )
#         # TODO - work with the authentication backend
#         user = authenticate(username=email, password=password)
#
#         if user is None:
#             raise serializers.ValidationError(
#                 'User was not found.'
#             )
#
#         if not user.is_active:
#             raise serializers.ValidationError(
#                 'This user has been deactivated.'
#             )
#
#         return {
#             'email': user.email,
#             'username': user.username,
#             'token': user.token
#         }


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'bio', 'image', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()

        return user

    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            if key == 'password':
                instance.set_password(value)
            else:
                setattr(instance, key, value)
        instance.save()
        return instance


class ProfileSerializer(serializers.ModelSerializer):
    following = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['username', 'bio', 'image', 'following']

    def get_following(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return obj.followers.filter(pk=user.id).exists()
        return False

    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return instance

    def to_representation(self, instance):
        data = super().to_representation(instance)
        return {'profile':data}


class ArticleSerializer(serializers.ModelSerializer):

    author = serializers.SerializerMethodField(read_only=True)
    tagList = serializers.SlugRelatedField(many=True, slug_field='tag', queryset=Tag.objects.all())
    favorited = serializers.SerializerMethodField(read_only=True)
    favoritesCount = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Article
        fields = ['slug', 'title', 'description', 'body', 'tagList', 'createdAt', 'updatedAt', 'favorited', 'favoritesCount', 'author']
        read_only_fields = ['slug', 'createdAt', 'updatedAt', 'author']

    def get_author(self, obj):
        request = self.context.get('request')
        serializers = ProfileSerializer(obj.author, context={'request': request})
        return serializers.data['profile']

    def get_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return obj.favorites.filter(pk=user.id).exists()
        return False

    def get_favoritesCount(self, obj):
        return obj.favorites.all().count()

    def create(self, validated_data):
        tagList = validated_data.pop('tagList')
        article = Article(author=self.context['request'].user, **validated_data)
        article.save()
        article.tagList.add(*tagList)

        return article


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField(read_only=True)
    id = serializers.IntegerField(source='pk', read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'createdAt', 'updatedAt', 'body', 'author']

    def get_author(self, obj):
        request = self.context.get('request')
        serializers = ProfileSerializer(obj.author, context={'request': request})
        return serializers.data['profile']

    def create(self, validated_data):
        comment = Comment(author=self.context['request'].user, article=self.context['article'], **validated_data)
        comment.save()

        return comment

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['tag']