from django.contrib import admin
from .models import Post, LikePost, DislikePost

admin.site.register(Post)
admin.site.register(LikePost)
admin.site.register(DislikePost)
