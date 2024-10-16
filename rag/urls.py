from django.urls import path
from .views import post_query

urlpatterns = [
    path('query/', post_query),
]
