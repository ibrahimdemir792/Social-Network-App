import json
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.core.serializers import serialize
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .models import User, Post, Profile
from .models import Profile


def index(request):
    if not request.user.is_authenticated:
        return render(request, "network/index.html")
    else:
        profile = Profile.objects.get(user=request.user)
        return render(request, "network/index.html", {
            "profile": profile.serialize()
        })


def following(request):
    profile = Profile.objects.get(user=request.user)
    return render(request, "network/following.html", {
        "profile": profile.serialize()
    })


def profile(request, user_id):
    profile = Profile.objects.get(user=user_id)
    posts = Post.objects.filter(author=user_id)
    return render(request, "network/profile.html", {
        "profile": profile.serialize(),
        "posts": [post.serialize() for post in posts],
        "user_id": user_id
    })


def login_view(request):
    if request.method == "POST":
        # Check if the user is trying to sign in or sign up
        if 'sign_in' in request.POST:

            # Attempt to sign user in
            username = request.POST["username"]
            password = request.POST["password"]
            user = authenticate(request, username=username, password=password)

            # Check if authentication successful
            if user is not None:
                login(request, user)
                return HttpResponseRedirect(reverse("index"))
            else:
                return render(request, "network/login.html", {
                    "message": "Invalid username and/or password."
                })
        elif 'sign_up' in request.POST:
            username = request.POST["username"]
            email = request.POST["email"]

            # Ensure password matches confirmation
            password = request.POST["password"]
            confirmation = request.POST["confirmation"]
            if password != confirmation:
                return render(request, "network/login.html", {
                    "message": "Passwords must match."
                })

            # Attempt to create new user
            try:
                user = User.objects.create_user(username, email, password)
                profile = Profile.objects.create(user=user)
                user.save()
                profile.save()
            except IntegrityError or ValueError:
                if IntegrityError:
                    return render(request, "network/login.html", {
                        "message": "Username already taken."
                    })
                elif ValueError:
                    return render(request, "network/login.html", {
                        "message": "Username must be set"
                    })
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

def new_post(request):
    if request.method == "POST":
        content = request.POST["postContent"]
        user = request.user
        post = Post.objects.create(author=user, content=content)
        post.save()
        return HttpResponseRedirect(reverse("index"))


def like(request, post_id):
    if request.method == "PUT":
        data = json.loads(request.body)
        action = data.get("action")
        if action == "like" or action == "unlike":
            try:
                post = Post.objects.get(pk=post_id)
            except Post.DoesNotExist:
                return JsonResponse({"error": "Post not found."}, status=404)
            
            if action == "like":
                post.likes.add(request.user)
            elif action == "unlike":
                post.likes.remove(request.user)

            post.save()
            return JsonResponse(post.serialize())
        return JsonResponse({"error": "Invalid action."}, status=400)
    return JsonResponse({"error": "PUT request required."}, status=400)

def comment(request):
    pass

def follow(request, profile_id):
    if request.method == "PUT":
        data = json.loads(request.body)
        followStatus = data.get("followStatus")
        if followStatus == "isFollowing" or followStatus == "isNotFollowing":
            try:
                profileOwner = Profile.objects.get(user=request.user)
                profileVisited = Profile.objects.get(pk=profile_id)
            except Profile.DoesNotExist:
                return JsonResponse({"error": "Profile not found."}, status=404)
            
            if followStatus == "isFollowing":
                profileOwner.following.remove(profileVisited.user)
                profileVisited.followers.remove(request.user)

            elif followStatus == "isNotFollowing":
                profileOwner.following.add(profileVisited.user)
                profileVisited.followers.add(request.user)

            profileOwner.save()
            profileVisited.save()
            return JsonResponse(profileVisited.serialize())
        return JsonResponse({"error": "Invalid follow status."}, status=400)
    return JsonResponse({"error": "PUT request required."}, status=400)

def load_posts(request, pageTitle, user_id, page=1):
    """
    Specify the page title and user id to load the posts with filters before pagination
    By the way, filtering before pagination prevents empty pages from being displayed
    """
    all_posts = Post.objects.order_by("-created_at").all()
    if user_id == 0:
        if pageTitle == "Social_Network":
            posts = all_posts.all()
        elif pageTitle == "following":
            posts = all_posts.filter(author__in=request.user.profile.following.all())
    else:
        if pageTitle == "Network_Profile_Page":
            posts = all_posts.filter(author=user_id)
            # .filter(post => post.author.username==profile.user)

    # Pagination
    paginator = Paginator(posts, 10) # Show 10 posts per page
    try:
        current_page = int(page)
        posts = paginator.page(current_page)
    except PageNotAnInteger:
        posts = paginator.page(1)
        current_page = 1
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
        current_page = paginator.num_pages

    serialized_posts = [post.serialize() for post in posts]
    total_pages = paginator.num_pages

    return JsonResponse({
        'posts': serialized_posts,
        'current_page': current_page,
        'total_pages': total_pages,
    })


def edit_post(request, post_id):
    if request.method == "PUT":
        data = json.loads(request.body)
        newContent = data.get("newContent")
        try:
            post = Post.objects.get(pk=post_id)
            post.content = newContent
            post.save()
            return JsonResponse({"message": "Post updated successfully."}, status=200)
        except Post.DoesNotExist:
            return JsonResponse({"error": "Post not found."}, status=404)
    return JsonResponse({"error": "PUT request required."}, status=400)


def edit_profile(request):
    if request.method == "POST":
        profile = Profile.objects.get(user=request.user)

        # Get new bio and profile pic from the form
        newbio = request.POST["bio"]
        newProfilePic = request.POST["profile_pic"]

        # Update the profile
        profile.profile_pic = newProfilePic
        profile.bio = newbio
        profile.save()
        return HttpResponseRedirect(reverse("profile", args=(request.user.id,)))
    else:
        return render(request, "network/edit_profile.html")
