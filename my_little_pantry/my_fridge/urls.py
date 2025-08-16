from django.urls import path
from .views import fridge_view, add_fridge_product, shopping_list, remove_fridge_product  # importujemy widok

urlpatterns = [
    path('', fridge_view, name='fridge'),  # /fridge/ będzie uruchamiać fridge_view
    path('add/', add_fridge_product, name='add_fridge_product'), # /fridge/add/
    path('remove/', remove_fridge_product, name='remove_fridge_product'),# /fridge/remove/
]

# to bedzie w aplikacji my_shopping_list
    # path('list/', shopping_list, name='shopping_list')