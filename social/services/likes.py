from django.db.models import Q, Count
from django.shortcuts import get_object_or_404
from rest_framework import status
from datetime import date

from ..models import LikePost, DislikePost, Post


def like_post(post_id: int, current_user_id: int) -> dict:
    post = get_object_or_404(Post, id=post_id)

    existing_like = LikePost.objects.filter(user_id=current_user_id, post=post)

    existing_dislike = DislikePost.objects.filter(user_id=current_user_id, post=post)

    if existing_like.exists():
        existing_like.delete()
        return {'message': 'Post unliked', 'status': status.HTTP_200_OK}

    else:
        if existing_dislike.exists():
            existing_dislike.delete()
        LikePost.objects.create(user_id=current_user_id, post=post)

        return {'message': 'Post liked', 'status': status.HTTP_200_OK}


def get_likes_aggregated_by_days(date_from: date, date_to: date) -> LikePost:
    aggregated_likes = LikePost.objects.filter(Q(liked_at__gte=date_from) & Q(liked_at__lte=date_to)). \
        extra(select={'day': "TO_CHAR(liked_at, 'YYYY-MM-DD')"}).values('day').annotate(total_likes=Count('id'))

    return aggregated_likes
