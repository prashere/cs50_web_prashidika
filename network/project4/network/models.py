from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Post(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posted_by')
    content = models.CharField(max_length=300, blank=False,null=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Post : {self.id} made by {self.creator.username}"

class Likes(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post')

    def __str__(self):
        return f"User: {self.user.username} liked {self.post}"

class Follower(models.Model):
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followed_by_users')
    follower= models.ForeignKey(User, on_delete=models.CASCADE, related_name='following_users')

    def __str__(self):
        return f'{self.follower.username} follows {self.following.username}'
    
