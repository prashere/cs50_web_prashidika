from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect,JsonResponse
from django.shortcuts import render
from django.urls import reverse

from .models import User,Post,Follower,Likes

import json
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

from django.core.paginator import Paginator


def index(request):
     posts_per_page = 10

     posts = Post.objects.all()
     # Ordering all the created posts in reverse chronological order
     posts = posts.order_by('-created_at').all()

    # Implementing paginator class
     paginator = Paginator(posts,posts_per_page)
     page_number = request.GET.get('page')
     page = paginator.get_page(page_number)

     return render(request, "network/index.html",{'page':page})

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
    

@csrf_exempt
@login_required   
def new_post(request):
    """
    Creates and saves a new post for a authenticated user
    """
    user = request.user # get the user
    if request.method != "POST":
        return JsonResponse({'error':'POST request required'}, status_code = 400)
    
    data = json.loads(request.body.decode('utf-8'))
    content = data.get('content','')
    # Creating a new Post object and saving it
    post = Post(creator = user, content=content)
    post.save()

    return JsonResponse({"message": "Post successfully created"}, status=201)


@login_required
@csrf_exempt
def save_edited_post(request,post_id):
    """
    Gets the new contents for a created post and changes the content to the new edited content
    """
    if request.method != "POST":
        return JsonResponse({'error':'POST request required'}, status_code = 400)
    
    data = json.loads(request.body.decode('utf-8'))
    content = data.get('content','')
    try:
        post = Post.objects.get(pk=post_id) # Getting the post with given post_id
    except :
        return JsonResponse({'error': 'Post not found'}, status_code = 404)
    
    post.content = content # Replacing the content of the post with new content
    post.save() # Saving the post 

    return JsonResponse({"message": "Post successfully created"}, status=201)


def profile(request,username):
    """
    Renders a user's profile page, including their posts,
    follower count, and following count. It also checks if the currently logged-in user is
    following the profile owner.
    """
    posts_per_page = 10
    creator = User.objects.get(username = username)

    if request.user.is_authenticated:
        user = request.user
        try:
            test_follower = Follower.objects.get(following=creator, follower=user)
            is_following = True
        except Follower.DoesNotExist:
            is_following = False
    else:
        is_following = None
    
    following = creator.following_users.count()
    follower = creator.followed_by_users.count()

    posts = Post.objects.filter(creator = creator)
    # Ordering the posts in reverse chronological order
    posts.order_by('-created_at').all()

    paginator = Paginator(posts,posts_per_page)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    return render(request, 'network/profile.html',
                  {'following':following,
                   'follower' :follower,
                   'page':page,
                   'creator':creator,
                   'is_following':is_following})

@login_required
@csrf_exempt
def add_follower(request,creator_id):
    """
    It allows the currently logged-in user to follow another user's profile.
    """
    creator = User.objects.get(pk=creator_id)
    user = request.user

    follow_obj = Follower(following = creator, follower = user)
    follow_obj.save()

    return JsonResponse({'message':'Successfully followed'},status =201)

    
@login_required
@csrf_exempt
def remove_follower(request,creator_id):
    """
    It allows the currently logged-in user to unfollow another user's profile
    """
    creator = User.objects.get(pk=creator_id)
    user = request.user

    follow_obj = Follower.objects.filter(following = creator, follower = user)
    follow_obj.delete()

    return JsonResponse({'message':'Successfully unfollowed'},status =201)

@login_required
def following_posts(request):
    """
    Renders a page consisting of posts made by creators followed by 
    the current user
    """
    posts_per_page = 10

    user = request.user
    posts = []

    followings = user.following_users.all()

    for anyone in followings:
        currentPost = Post.objects.filter(creator = anyone.following)
        posts.extend(currentPost)

    all_posts = Post.objects.filter(pk__in=[post.pk for post in posts])
    all_posts = all_posts.order_by('-created_at').all()

    paginator = Paginator(all_posts,posts_per_page)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    return render(request, 'network/following.html',
                  {'page':page})

@csrf_exempt
@login_required
def like_post(request,post_id,user_id):
    """
    It allows a logged-in user to like a specific post by its ID.
    """
    if request.method != 'POST':
        return JsonResponse({'error':'POST request required '},status = 400)
    
    user = User.objects.get(pk=user_id)
    post = Post.objects.get(pk=post_id)

    like_obj = Likes(user = user, post=post)
    like_obj.save()

    like_count = (Likes.objects.filter(post=post)).count()

    return JsonResponse({'message':'Successfully added like','like_count':like_count},status = 200)


@csrf_exempt
@login_required
def unlike_post(request,post_id,user_id):
    """
    It allows a logged-in user to remove like from a specific post by its ID.
    """
    if request.method != 'POST':
        return JsonResponse({'error':'POST request required '},status = 400)
    
    user = User.objects.get(pk=user_id)
    post = Post.objects.get(pk=post_id)

    try:
        like_obj = Likes.objects.filter(user=user, post=post)
        like_obj.delete()

        like_count = (Likes.objects.filter(post=post)).count()

        return JsonResponse({'message':'Successfully removed like','like_count':like_count},status = 200)
    except:
        return JsonResponse({'error': 'No like object found'}, status = 404)

@csrf_exempt
def post_preload_loggedOut(request, post_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST request required'}, status=400)  
    post = Post.objects.get(pk = post_id)
    like_count = Likes.objects.filter(post=post).count()
    return JsonResponse({'message': 'Fetch Success', 'like_count': like_count}, status=200)


@csrf_exempt
def post_preload(request, post_id, user_id):
    """
    It allows a user to retrieve preloaded information about a specific post 
    such as whether the user has liked the post and the total like count for the post.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST request required'}, status=400)
    try:
        user = User.objects.get(pk=user_id)
        post = Post.objects.get(pk=post_id)
        # Checking if the user has already liked the post
        is_liked = Likes.objects.filter(user=user, post=post).exists()
        # Counting the total likes for the post
        like_count = Likes.objects.filter(post=post).count()
        return JsonResponse({'message': 'Fetch Success', 'is_liked': is_liked, 'like_count': like_count}, status=200)
    except:
        return JsonResponse({'error': 'User or Post does not exist'}, status=404)