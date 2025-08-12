from django.urls import path
from .views import fridge_view  # importujemy widok

urlpatterns = [
    path('fridge/', fridge_view, name='fridge'),  # /fridge/ będzie uruchamiać fridge_view
]