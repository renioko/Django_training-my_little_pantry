from django.urls import path
from .views import shopping_list, add_product_to_shopping_list, remove_shopping_products

urlpatterns = [
    path('', shopping_list, name='shopping_list'),
    path('add/', add_product_to_shopping_list, name='add_product_to_shopping_list'),
    path('remove/', remove_shopping_products, name='remove_shopping_products'),
]