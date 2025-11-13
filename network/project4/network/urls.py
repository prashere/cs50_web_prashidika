
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path('profile/<str:username>', views.profile, name='profile'),
    path('following', views.following_posts,name='following'),

    #API routes
    path('posts', views.new_post, name='post'),
    path('follow/<int:creator_id>',views.add_follower, name='add_follower'),
    path('unfollow/<int:creator_id>',views.remove_follower, name='remove_follower'),
    path('edit/<int:post_id>', views.save_edited_post, name='save_post'),
    path('like/<int:post_id>/<int:user_id>',views.like_post, name='like'),
    path('unlike/<int:post_id>/<int:user_id>',views.unlike_post, name='unlike'),
    path('loadlikes/<int:post_id>/<int:user_id>',views.post_preload,name='load_likes'),
    path('loadlikes/<int:post_id>', views.post_preload_loggedOut, name='load_likes_loggedOut')
]
