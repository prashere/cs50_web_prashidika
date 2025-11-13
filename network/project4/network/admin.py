from django.contrib import admin

from .models import Post, User, Likes, Follower

# Register your models here.
admin.site.register(Post)
admin.site.register(Likes)
admin.site.register(Follower)
admin.site.register(User)
