from django.contrib import admin
from .models import Post, LikePost, DislikePost, SocialProfile

admin.site.register(Post)
admin.site.register(SocialProfile)
admin.site.register(LikePost)
admin.site.register(DislikePost)
