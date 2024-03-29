from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("wiki/<str:title>", views.load_wiki, name="wiki"),
    path("create", views.create_wiki, name="create"),
    path("wiki/edit/<str:title>", views.update_wiki, name="update"),
    path("random", views.random_wiki, name="random"),
]
