from django.contrib import admin
from .models import User, Profile, Post

# Register your models here.
admin.site.register(User)
admin.site.register(Profile)
admin.site.register(Post)

class PostAdmin(admin.ModelAdmin):
    filter_horizontal = ("likes",)