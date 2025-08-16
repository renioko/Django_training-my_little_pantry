from django.shortcuts import render

from django.contrib.auth.decorators import login_required

from my_fridge.models import Product, DefaultProduct
from .models import ShoppingListProduct, DefaultShoppingProduct
from my_fridge.views import index

# Create your views here.

# def index()

@login_required
def shopping_list(request):
    products = ShoppingListProduct.objects.filter(user=request.user)
    return render(request, 'shopping_list/shopping_list.html', context={'products': products})

