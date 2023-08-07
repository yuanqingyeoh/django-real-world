from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

# Create your models here.


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ['-updated_at', '-created_at']


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

#
# class Profile(models.Model):
#     username = models.CharField(max_length=255)
#     bio = models.TextField()
#     image = models.URLField()
#     # following - need a Following table?
#
#
# class Article(TimeStampedModel):
#     slug = models.SlugField(max_length=255, unique=True)
#     title = models.CharField(max_length=255)
#     description = models.TextField()
#     body = models.TextField()
#     tags = models.ManyToManyField('Tag', related_name='articles')
#     author = models.ForeignKey('Profile', on_delete=models.CASCADE, related_name='articles')
#
#
# class Comment(TimeStampedModel):
#     body = models.TextField()
#
#     article = models.ForeignKey('Article', on_delete=models.CASCADE, related_name='comments')
#
#     author = models.ForeignKey('Profile', on_delete=models.CASCADE, related_name='comments')
#
#
# class Tag(TimeStampedModel):
#     tag = models.CharField(max_length=255)
#     slug = models.SlugField(unique=True)  # TODO find out why need this?
