from django.urls import path

from . import views

urlpatterns = [
    path('create-post/', views.CreatePost.as_view(), name="create_post"),
    path('get-posts/', views.GetPosts.as_view(), name="get_posts"),
    path('like-post/<int:post_id>/', views.LikePostView.as_view(), name="like_post"),
    path('dislike-post/<int:post_id>/', views.DislikePostView.as_view(), name="dislike_post"),
    path('likes-analytics/', views.LikesAnalytics.as_view(), name="likes_analytics"),
    path('dislikes-analytics/', views.DislikesAnalytics.as_view(), name="dislikes_analytics")
]
