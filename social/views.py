from authentication.services.authentication_rules import JWTAuthTokenRequired
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from .models import Post, SocialProfile
from .serializers import PostSerializer, LikesAnalyticsSerializer, DislikesAnalyticsSerializer, \
    AnalyticsDatesSerializer, UserLastActivitySerializer
from .services.dislikes import dislike_post, get_dislikes_aggregated_by_days
from .services.likes import like_post, get_likes_aggregated_by_days

User = get_user_model()


class GetPosts(generics.ListAPIView):
    # Get list of all posts (with pagination)
    queryset = Post.objects.all()
    authentication_classes = [JWTAuthTokenRequired]
    permission_classes = [IsAuthenticated]
    serializer_class = PostSerializer


class CreatePost(generics.CreateAPIView):
    # Creating new post
    permission_classes = [IsAuthenticated]
    serializer_class = PostSerializer

    # Overriding create method, for custom functionality
    def create(self, request, *args, **kwargs):
        serializer = PostSerializer(data=request.data)

        if serializer.is_valid():
            data = request.data

            author = User.objects.get(id=data.get('author'))
            new_post = Post.objects.create(title=data['title'], body=data['body'],
                                           author=author)

            serializer = PostSerializer(new_post)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
        auth_class = JWTAuthTokenRequired()

        authentication_result = auth_class.authenticate(request=request)

        if not authentication_result:
            return {'detail': 'Invalid access token', 'status': status.HTTP_400_BAD_REQUEST}

        current_user_id = authentication_result[1]['user_id']

        like_post_response = like_post(post_id, current_user_id)

        return Response(like_post_response, status=like_post_response['status'])


class DislikePostView(generics.GenericAPIView):
    # Dislike post logic
    permission_classes = [IsAuthenticated]
    serializer_class = PostSerializer

    def post(self, request, post_id):
        auth_class = JWTAuthTokenRequired()

        authentication_result = auth_class.authenticate(request=request)

        if not authentication_result:
            return {'detail': 'Invalid access token', 'status': status.HTTP_400_BAD_REQUEST}

        current_user_id = authentication_result[1]['user_id']

        dislike_post_response = dislike_post(post_id, current_user_id)

        return Response(dislike_post_response, status=dislike_post_response['status'])


class LastUserActivity(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserLastActivitySerializer
    lookup_field = "user_id"

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        user = get_object_or_404(User, id=user_id)
        social_profile = SocialProfile.objects.filter(user=user)
        return social_profile
