import datetime

from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Post(models.Model):
    title = models.CharField(max_length=150, null=False)
    body = models.TextField(null=False)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class LikePost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, related_name="likes")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes")
    liked_at = models.DateField(default=datetime.datetime.utcnow)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'post'], name="unique_like"),
        ]

    def __str__(self):
        return self.user.username


class DislikePost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, related_name="dislikes")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="dislikes")
    disliked_at = models.DateField(default=datetime.datetime.utcnow)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'post'], name="unique_dislike"),
        ]

    def __str__(self):
        return self.user.username


class SocialProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.PROTECT, null=False)
    last_activity = models.DateTimeField(default=datetime.datetime.utcnow)

    def __str__(self):
        return self.user.username + ' - ' + str(self.last_activity)
