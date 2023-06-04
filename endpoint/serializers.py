from rest_framework import serializers
from endpoint.models import User, Profile, Article, Tag


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'token', 'username', 'bio', 'image']


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['username', 'bio', 'image']


class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ['slug', 'title', 'description', 'body', 'createdAt', 'updatedAt']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['tag']