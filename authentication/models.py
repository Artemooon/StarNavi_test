from django.contrib.auth.models import AbstractUser
from django.db import models
from datetime import datetime


class SocialProfile(AbstractUser):
    last_activity = models.DateTimeField(default=datetime.utcnow)

