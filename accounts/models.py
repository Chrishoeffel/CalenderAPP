import os

from django.contrib.auth.models import AbstractUser, User
from django.contrib.auth.models import UnicodeUsernameValidator
from django.core.validators import MinLengthValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class Avatar(models.Model):
    photo = models.ImageField(upload_to="avatars")

    def __str__(self):
        return os.path.basename(self.photo.name)


class User(AbstractUser):
    username = models.CharField(
        _("username"),
        max_length=150,
        unique=True,
        help_text=_(
            "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
        ),
        validators=[UnicodeUsernameValidator(), MinLengthValidator(3)],
        error_messages={"unique": _("A user with that username already exists."),},
    )
    avatar = models.ForeignKey(
        "Avatar", null=True, blank=True, on_delete=models.PROTECT
    )
    is_guest = models.BooleanField(default=False)

    class Meta:
        ordering = ["-id"]
class Profile(models.Model):
    
    user = models.OneToOneField(User, related_name="profile", on_delete=models.CASCADE)
    first_name = models.CharField(max_length=30, blank=False)
    last_name = models.CharField(max_length=30, blank=False)
    email = models.EmailField(max_length=50, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)        

    class Meta:
        verbose_name = _('Profile')
        verbose_name_plural = _('Profiles')
class Calendar_Event(models.Model):
    name = models.ForeignKey(Profile, on_delete=models.CASCADE, serialize=True, max_length=100, blank=True)
    event_date = models.DateField(auto_now_add=True)
    time = models.DurationField(max_value=None, min_value=None)
    update = models.DateTimeField(auto_now=True)
    location = models.CharField(max_length=120)
    decription = models.CharField(blank=True, max_length=300)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name