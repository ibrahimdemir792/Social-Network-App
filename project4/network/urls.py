
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("new_post", views.new_post, name="new_post"),
    path("following", views.following, name="following"),
    path("profile/<int:user_id>", views.profile, name="profile"),
    path("edit_profile", views.edit_profile, name="edit_profile"),

    # API Routes
    path("load_posts/<str:pageTitle>/<int:user_id>/<int:page>", views.load_posts, name="load_posts"),
    path("like/<int:post_id>", views.like, name="like"),
    path("follow/<int:profile_id>", views.follow, name="follow"),
    path("comment/<int:post_id>", views.comment, name="comment"),
    path("edit_post/<int:post_id>", views.edit_post, name="edit_post"),
]
