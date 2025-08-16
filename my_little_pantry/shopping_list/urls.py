from django.urls import path
from .views import shopping_list

urlpatterns = [
    path('', shopping_list, name='shopping_list'),
]