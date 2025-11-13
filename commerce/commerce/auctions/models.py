from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Listing(models.Model):
    category_choices = [
        ('Art & Decor','Art & Decor'),
        ('Accesory','Accesory'),
        ('Fashion','Fashion'),
        ('Home','Home'),
        ('Electronics','Electronics'),
    ]
    title = models.CharField(max_length=70)
    description = models.CharField(max_length = 400)
    starting_bid = price = models.DecimalField(max_digits=20,decimal_places=2)
    price = models.DecimalField(max_digits=20,decimal_places=2)
    image = models.CharField(max_length = 900,blank=True,null=True)
    category = models.CharField(max_length=20,choices=category_choices,null=True,blank=True)
    owner = models.ForeignKey(User,on_delete=models.CASCADE,related_name='seller')
    created_at = models.DateTimeField(auto_now_add=True)
    watchlist = models.ManyToManyField(User, blank=True, related_name='listing')
    is_closed = models.BooleanField()
    winner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='winner',blank=True,null=True)

    def __str__(self) -> str:
        return f"Item:{self.title} Owner:{self.owner}"

class Bid(models.Model):
    bidder = models.ForeignKey(User,on_delete=models.CASCADE,related_name='buyer')
    item = models.ForeignKey(Listing,on_delete=models.CASCADE,related_name="bid_item")
    bid_price = models.DecimalField(max_digits=20,decimal_places=2)
    bid_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Bid {self.bid_price} on {self.item}"

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="commenter")
    auction_item = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comment_item")
    comment_text = models.CharField(max_length=100)
    comment_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self) -> str:
        return f"{self.comment_text} on {self.auction_item}"


