from django.contrib.auth import get_user_model
from rest_framework import generics
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from .models import Post
from .serializers import PostSerializer, LikesAnalyticsSerializer, DislikesAnalyticsSerializer, AnalyticsDatesSerializer
from .services.dislikes import dislike_post, get_dislikes_aggregated_by_days
from .services.likes import like_post, get_likes_aggregated_by_days

User = get_user_model()


# Fix date serialization, like dislike , create method, user app, check last_login, validate data in serializers
class GetPosts(generics.ListAPIView):
    # Get list of all posts (with pagination)
    queryset = Post.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = PostSerializer


class CreatePost(generics.CreateAPIView):
    # Creating new post
    permission_classes = [IsAuthenticated]
    serializer_class = PostSerializer


class LikesAnalytics(generics.ListAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = LikesAnalyticsSerializer

    def get_queryset(self):
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        dates_serializer = AnalyticsDatesSerializer(data=self.request.query_params)
        dates_serializer.is_valid(raise_exception=True)

        return get_likes_aggregated_by_days(date_from, date_to)


class DislikesAnalytics(generics.ListAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = DislikesAnalyticsSerializer

    def get_queryset(self):
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        dates_serializer = AnalyticsDatesSerializer(data=self.request.query_params)
        dates_serializer.is_valid(raise_exception=True)

        return get_dislikes_aggregated_by_days(date_from, date_to)


class LikePostView(generics.GenericAPIView):
    # Like post logic
    permission_classes = [IsAuthenticated]
    serializer_class = PostSerializer

    def post(self, request, post_id):
        if not request.user.is_authenticated:
            return {'detail': 'Invalid access token', 'status': status.HTTP_400_BAD_REQUEST}

        current_user_id = request.user.id

        like_post_response = like_post(post_id, current_user_id)

        return Response(like_post_response, status=like_post_response['status'])


class DislikePostView(generics.GenericAPIView):
    # Dislike post logic
    permission_classes = [IsAuthenticated]
    serializer_class = PostSerializer

    def post(self, request, post_id):
        if not request.user.is_authenticated:
            return {'detail': 'Invalid access token', 'status': status.HTTP_400_BAD_REQUEST}

        current_user_id = request.user.id

        dislike_post_response = dislike_post(post_id, current_user_id)

        return Response(dislike_post_response, status=dislike_post_response['status'])

