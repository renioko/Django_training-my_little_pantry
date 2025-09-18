from django.urls import path
from .views import shopping_list, add_product_to_shopping_list, remove_shopping_products, remove_default, remove_all, ListShoppingProductsView, UpdateShoppingProducts, ListShoppingProductsAPIView

urlpatterns = [
    path('', shopping_list, name='shopping_list'),
    path('add/', add_product_to_shopping_list, name='add_product_to_shopping_list'),
    path('remove/', remove_shopping_products, name='remove_shopping_products'),
    path('remove_default/', remove_default, name='remove_default'),
    path('update/', ListShoppingProductsView.as_view(), name='update'),
    path('edit_product/<int:pk>', UpdateShoppingProducts.as_view(), name='edit_product'),
    path('remove_all', remove_all, name='remove_all'),
    path('test', ListShoppingProductsAPIView.as_view(), name='test')
]