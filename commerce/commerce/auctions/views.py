from django.contrib.auth import authenticate, login,logout
from django.contrib import messages
from django.db import IntegrityError
from django.http import  HttpResponseRedirect
from django.shortcuts import render,redirect
from django.urls import reverse
from decimal import Decimal

from .models import User,Listing,Comment,Bid

from django.contrib.auth.decorators import login_required


def index(request):
    return render(request, "auctions/index.html")


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
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


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
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
    

def create_listing(request):
    if request.method == 'POST':
        # Fetches all the input data of the form
        title=request.POST['title']
        description = request.POST['description']
        price=request.POST['price']
        image=request.POST['image-url']
        category=request.POST.get('category')
        # Gets the current logged in user
        owner=request.user
        # Creates a new listing and saves it
        listing = Listing(title=title, description=description,starting_bid=price, price=price, image=image, category=category, owner=owner, is_closed = False)
        listing.save()
        # Redirects to the created listing page after saving it
        return redirect('individual_listing',id=listing.id,title=listing.title)
    return render(request, 'auctions/create_listing.html',
                  {'categories':Listing.category_choices})

def active_listings(request):
    # Fetches all the active listing objects of Listing module and renders a page displaying them
    listings = Listing.objects.filter(is_closed = False)
    return render(request, 'auctions/index.html',
                  {'listings':listings})

def closed_listings(request):
    # Fetches all the closed listing objects of Listing module and renders a page displaying them
    listings = Listing.objects.filter(is_closed = True)
    return render(request, 'auctions/closed.html',
                  {'listings':listings})


def close_listing(listing,bids):
    """
    Calculates the maximum bid for a listing , fetches the bidder of the corresponding bid.
    Saves the bidder as the listing's winner and closes the listing.
    If no bids were made, sets the listing's winner as the owner itself.
    """
    maxs=0 # Initializing maxs to 0
    if not listing.is_closed:
        if bids:
            for bid in bids:
                if bid.bid_price > maxs:
                    maxs=bid.bid_price
            for bid in bids:
                if maxs == bid.bid_price:
                    listing.winner = bid.bidder
                    listing.is_closed = True
                    listing.save()
        else:
            listing.winner = listing.owner
            listing.is_closed = True
            listing.save()


def individual_listing(request, id, title):
    """
    Display detailed information about an individual listing, allowing users to place bids,
    close the listing, and add comments.
    """
    can_bid = None  # Initializing can_bid as 0
    user = request.user # Fetching the current user
    try:
        listing = Listing.objects.get(pk=id, title=title)
    except Listing.DoesNotExist:
        return render(request, 'auctions/indi_listing.html', {'message': "Listing doesn't exist"})
    all_comments = listing.comment_item.all()
    found_listing = listing.watchlist.filter(id=user.id).exists() 
    bids = listing.bid_item.all()
    bids_count = bids.count()
    is_owner = user == listing.owner
    max_bid_amount = max(bids.values_list('bid_price', flat=True), default=0) # Calculating the maximum bid_price
    comment_text = None # Initializing comment_text as None

    if request.method == 'POST':
        action = request.POST.get('action')
        # When the user submits a bid
        if action == 'bid':
            new_bid = Decimal(request.POST['new_bid'])
            if new_bid >= listing.price and new_bid > max_bid_amount:
                # Updating the price as the new bid
                listing.price = new_bid
                listing.save()
                # Creating and saving the new bid entry
                new_entry = Bid(bidder=user, item=listing, bid_price=new_bid)
                new_entry.save()
                can_bid = True
                messages.success(request, " Successfully added !") 
            else:
                can_bid = False
                messages.error(request, "Error! Enter higher bid than previous ones.")
            return HttpResponseRedirect(reverse('individual_listing',args=[id,title]))
        # When the owner closes the listing
        elif action == 'close':
           if 'close_listing' in request.POST:
            close_listing(listing,bids)
        # When the user posts a comment
        elif action == 'comment-check':
            comment_text = request.POST.get('comment')
            if comment_text:
                new_comment = Comment(user=user, auction_item = listing, comment_text = comment_text)
                new_comment.save()
    return render(request, 'auctions/indi_listing.html', 
                  {'item': listing,
                   'can_bid': can_bid,
                   'found_listing': found_listing,
                   'is_owner': is_owner,
                   'bids': bids,
                   'bids_count': bids_count,
                   'all_comments':all_comments
                   })


@login_required
def toggle_watchlist(request,id,title):
    current_listing = Listing.objects.get(pk=id)
    user = request.user
    if current_listing in user.listing.all():
        current_listing.watchlist.remove(user)
    else:
        current_listing.watchlist.add(user)
    return HttpResponseRedirect(reverse('individual_listing', args=[id,title]))

@login_required
def watchlist(request):
    """
    Fetches all the listings in watchlist of a user and renders a watchlist page 
    Only for authenticated users.
    """
    user= request.user
    current_watchlist = user.listing.all()
    return render(request, 'auctions/watchlist.html', 
                  {'current_watchlist':current_watchlist})


def category(request, title = None):
    """
    Displays a page rendering a list of active listings based on a specific category.
    """
    choices = Listing.category_choices
    listings = None # Initializing listings as None
    if title:
        listings = Listing.objects.filter(category = title,is_closed=False)
    return render(request, 'auctions/category.html ',
                  {'choices':choices,
                   'listings':listings,
                   'active_category':title})


