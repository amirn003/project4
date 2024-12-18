from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Post


def index(request):
    posts = Post.objects.all().filter().order_by("-date")
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
    user = User.objects.get(username=username)
    posts = Post.objects.all().filter(user=user).order_by("-date")
    following = user.following.all().count()
    followers = user.followers.all().count()
    current_user = request.user
    is_following = False
    authenticated = False
    if request.user.is_authenticated:
        current_user_id = request.user.id
        is_following = request.user.following.filter(id=current_user_id).exists()
        authenticated = True
    return render(request, "network/profile.html", {
        "user": user,
        "posts": posts,
        "is_following": is_following,
        "authenticated": authenticated,
        "current_user": current_user,
        "following": following,
        "followers": followers
    })

def follow(request, username):
    user = User.objects.get(username=username)
    current_user = request.user
    current_user_id = current_user.id
    is_following = current_user.following.filter(id=current_user_id).exists()
    if is_following:
        current_user.following.remove(user)
    else:
        current_user.following.add(user)
    return HttpResponseRedirect(reverse("profile", args=(username,)))


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
