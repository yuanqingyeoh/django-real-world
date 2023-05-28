from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

# Create your models here.


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class UserManager(BaseUserManager):

    def create_user(self, username, email, password=None):
        if username is None:
            raise TypeError("User must have a username")
        if email is None:
            raise TypeError("user must have an email address")

        user = self.model(username=username, email=self.normalize_email(email))
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, username, email, password):
        if password is None:
            raise TypeError("Superuser must have a password")

        user = self.model(username=username, email=self.normalize_email(email))
        user.set_password(password)
        user.is_staff = True
        user.is_superuser = True
        user.save()

        return user


class User(AbstractBaseUser):
    username = models.CharField(max_length=255)
    email = models.EmailField(unique=True)

    is_active = models.BooleanField(default=True)

    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    # token = models.TextField()

    objects = UserManager()

    def __str__(self):
        return self.email


class Profile(models.Model):
    username = models.CharField(max_length=255)
    bio = models.TextField()
    image = models.ImageField()
    # following - need a Following table?


class Article(TimeStampedModel):
    slug = models.SlugField(max_length=255, unique=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    body = models.TextField()
    tags = models.ManyToManyField('Tag', related_name='articles')
    author = models.ForeignKey('Profile', on_delete=models.CASCADE, related_name='articles')


class Comment(TimeStampedModel):
    body = models.TextField()

    article = models.ForeignKey('Article', on_delete=models.CASCADE, related_name='comments')

    author = models.ForeignKey('Profile', on_delete=models.CASCADE, related_name='comments')


class Tag(TimeStampedModel):
    tag = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)  # TODO find out why need this?
