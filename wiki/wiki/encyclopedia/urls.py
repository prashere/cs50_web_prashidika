from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("wiki/<str:title>", views.render_page, name="entry"),
    path("search/", views.search_result, name="search"),
    path("create/", views.create_entry_page, name='create'),
    path("new/", views.create_new_entry, name = 'entry_making'),
    path("edit/<str:title>", views.edit_entry, name='edit'),
    path("save/", views.save_entry, name='save'),
    path("random", views.random_entry, name='random_one')
]
