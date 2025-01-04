from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.core.paginator import Paginator

from .models import User, Post, Follow


def index(request):
    posts = Post.objects.all().filter().order_by("-date")
    posts = Paginator(posts, 10)
    page_number = request.GET.get('page')
    posts = posts.get_page(page_number)

    return render(request, "network/index.html", {
        "posts": posts
    })

def new_post(request):
    return render(request, "network/new_post.html")

def add_post(request):
    if request.method == "POST":
        content = request.POST["content"]
        current_user = request.user
        post = Post(user=current_user, content=content)
        post.save()
        return HttpResponseRedirect(reverse("index"))


def profile(request, username):
    user_profile = User.objects.get(username=username)
    posts = Post.objects.all().filter(user=user_profile).order_by("-date")
    # followers = user_profile.followers.all().count()
    followers = Follow.objects.filter(user=user_profile.id).count()

    posts = Paginator(posts, 10)
    page_number = request.GET.get('page')
    posts = posts.get_page(page_number)

    current_user = request.user
    current_user_id = request.user.id

    # following = user_profile.following.all().count()
    following = Follow.objects.filter(following=user_profile.id).count()

    if request.user.is_authenticated:
        is_following = Follow.objects.filter(user=user_profile, following=current_user).exists()

    return render(request, "network/profile.html", {
        "user_profile": user_profile,
        "posts": posts,
        "is_following": is_following,
        "current_user": current_user,
        "following": following,
        "followers": followers
    })


def follow(request, username):
    user = User.objects.get(username=username)
    current_user = request.user
    current_user_object = User.objects.get(id=current_user.id)
    current_user_id = current_user.id
    is_following = Follow.objects.filter(user=user, following=current_user).exists()
    if is_following:
        unfollow = Follow.objects.get(user=user.id, following=current_user.id)
        unfollow.delete()
        # current_user_object.following.remove(user)
        # return HttpResponse(f"<h1> UnFollow user: {user} </h1> ({current_user_object.following})")
    else:
        # current_user_object.following.add(user)
        follow = Follow(user= user, following= current_user_object)
        follow.save()
        # return HttpResponse(f"<h1> Follow user: {user} </h1> ({current_user_object.following})")

    return HttpResponseRedirect(reverse("profile", args=(username,)))

def following(request):
    current_user = request.user
    current_user_id = request.user.id
    posts = Post.objects.all().filter().order_by("-date")

    posts = Paginator(posts, 10)
    page_number = request.GET.get('page')
    posts = posts.get_page(page_number)

    posts_following = []
    for post in posts:
        if Follow.objects.filter(user=post.user, following=current_user).exists():
            posts_following.append(post)

    return render(request, "network/following.html", {
        "posts_following": posts_following
    })

def edit_post(request, post_id):
    post = Post.objects.get(id=post_id)
    return render(request, "network/edit_post.html", {
        "post": post
    })


def login_view(request):
    if request.method == "POST":

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
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")
