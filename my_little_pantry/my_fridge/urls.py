from django.urls import path
from .views import fridge_view, add_fridge_product, remove_fridge_product, check_expired_view, remove_expired_fridge_products # importujemy widok

urlpatterns = [
    path('', fridge_view, name='fridge'),  # /fridge/ będzie uruchamiać fridge_view
    path('add/', add_fridge_product, name='add_fridge_product'), # /fridge/add/
    path('remove/', remove_fridge_product, name='remove_fridge_product'),# /fridge/remove/
    path('expired/',check_expired_view, name='expired'), #fridge/remove_all_expired
    path('remove_expired', remove_expired_fridge_products, name='remove_expired')
]

# to bedzie w aplikacji my_shopping_list
    # path('list/', shopping_list, name='shopping_list')