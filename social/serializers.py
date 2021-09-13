from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Post, LikePost, DislikePost

User = get_user_model()


class PostSerializer(serializers.ModelSerializer):
    likes = serializers.SerializerMethodField()
    dislikes = serializers.SerializerMethodField()

    def get_likes(self, obj):
        return LikePost.objects.filter(post=obj).count()

    def get_dislikes(self, obj):
        return DislikePost.objects.filter(post=obj).count()

    class Meta:
        model = Post
        fields = ['id', 'title', 'body', 'author', 'created_at', 'likes', 'dislikes']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class LikesAnalyticsSerializer(serializers.ModelSerializer):
    total_likes = serializers.IntegerField()
    day = serializers.DateTimeField()

    class Meta:
        model = LikePost
        fields = ['total_likes', 'day']


class DislikesAnalyticsSerializer(serializers.ModelSerializer):
    total_dislikes = serializers.IntegerField()
    day = serializers.DateTimeField()

    class Meta:
        model = DislikePost
        fields = ['total_dislikes', 'day']


class AnalyticsDatesSerializer(serializers.Serializer):
    date_from = serializers.DateField(required=True)
    date_to = serializers.DateField(required=True)

    class Meta:
        fields = ['date_from', 'date_to']


class UserLastActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['user_id', 'last_activity', 'last_login']
