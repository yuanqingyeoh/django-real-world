from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.text import slugify

# Create your models here.


class TimeStampedModel(models.Model):
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ['-updatedAt', '-createdAt']


class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **other_fields):

        user = User(email=email, **other_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save()

        return user

    # def create_superuser(self, username, email, password):
    #     if password is None:
    #         raise TypeError("Superuser must have a password")
    #
    #     user = self.model(username=username, email=self.normalize_email(email))
    #     user.set_password(password)
    #     user.is_staff = True
    #     user.is_superuser = True
    #     user.save()
    #
    #     return user


class User(AbstractUser):

    # remove default fields
    first_name = None
    last_name = None

    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField(unique=True)
    bio = models.TextField(null=True, blank=True)
    image = models.URLField(null=True, blank=True)

    followers = models.ManyToManyField('self', blank=True, symmetrical=False)

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email

    def get_full_name(self):
        return self.name

    def get_short_name(self):
        return self.name


class Article(TimeStampedModel):
    slug = models.SlugField(max_length=255, unique=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    body = models.TextField()
    tagList = models.ManyToManyField('Tag', blank=True)
    favorites = models.ManyToManyField('User', blank=True)
    author = models.ForeignKey('User', on_delete=models.CASCADE, related_name='articles')

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        return super().save(*args, **kwargs)


class Comment(TimeStampedModel):
    body = models.TextField()

    article = models.ForeignKey('Article', on_delete=models.CASCADE, related_name='comments')

    author = models.ForeignKey('User', on_delete=models.CASCADE, related_name='comments')


class Tag(models.Model):
    tag = models.SlugField(unique=True)

    def __str__(self):
        return self.tag
