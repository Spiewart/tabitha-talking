from django.urls import path

from . import views

app_name = "blog"
urlpatterns = [
    path("search/", views.search_blog, name="search"),
]
