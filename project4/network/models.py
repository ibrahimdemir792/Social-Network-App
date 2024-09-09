from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    bio = models.TextField(max_length=256, blank=True)
    profile_pic = models.URLField(blank=True)
    followers = models.ManyToManyField(User, blank=True, related_name="followers")
    following = models.ManyToManyField(User, blank=True, related_name="following")

    def serialize(self):
        return {
            "id": self.id,
            "user": self.user.username,
            "bio": self.bio,
            "profile_pic": self.profile_pic,
            "followers": [user.username for user in self.followers.all()],
            "following": [user.username for user in self.following.all()],
            "followers_count": self.followers.count(),
            "following_count": self.following.count()
        }

    def __str__(self):
        return f"{self.user.username} Profile"

class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="post")
    content = models.TextField(max_length=144)
    likes = models.ManyToManyField(User, blank=True, related_name="liked_post")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def serialize(self):
        return {
            "id": self.id,
            "author": {
                "id": self.author.id,
                "username": self.author.username,
            },
            "content": self.content,
            "likes_count": self.likes.count(),
            "likes_who": [user.username for user in self.likes.all()],
            "created_at": self.created_at.strftime("%b %d %Y, %I:%M %p"),
            "updated_at": self.updated_at.strftime("%b %d %Y, %I:%M %p"),
        }

    def __str__(self):
        return f"{self.author.username} Posts"
    
class Comment(models.Model):
    comment = models.TextField(max_length=144),
    author = models.ForeignKey(User, on_delete=models.CASCADE),
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="post_comment"),

    def serialize(self):
        return {
            "id": self.id,
            "comment": self.comment,
            "author": self.author,
            "post": self.post
        }
    
    def __str__(self):
        return f"{self.author.username} comments"