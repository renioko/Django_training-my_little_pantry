from django.db.models import Sum, F
from django.shortcuts import render, redirect

from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .forms import AddShoppingProductForm, GenerateShoppingListActivate
from my_fridge.models import Product, DefaultProduct
from .models import ShoppingListProduct, DefaultShoppingProduct
from my_fridge.models import DefaultProduct, FridgeProduct
from my_fridge.views import index
from typing import List, Any, Set

# Create your views here.

# def index()

# 🚩 nie dodawane są default products do shopping list, chociaz sama lista sie wyswietla 
# 1. stworzyc nowego uzytkownika
# 2. dodac default products
# 3. po usunieciu z lodówki produkt powinien sie generowac w shopping list

# 🚩 w lodówce powiniejn byc przycisk 'usun przeterminowane produkty', ktory usunie je z lodówki (ale nie z Products i z defaults) i wyswietli liste produktów do usuniecia - ‼️ i poprosi o potwierdzenie ❗

def get_missing_products(user: Any) -> List[int]:
    """
    Checks if all DefaultProducts are in the fridge (FridgeProduct).
    Returns list of missing products as Product ids.
    """
    default_fridge_products = DefaultProduct.objects.filter(user=user)
    # values_list odwoluje sie do 'product'FK czyli do Product. dlatego nie uzywam 'id' tylko 'product' poniżej:
    products_in_fridge = FridgeProduct.objects.filter(user=user).values_list('product', flat=True)
    missing_products_ids = [product.product.id for product in default_fridge_products if product.product.id not in products_in_fridge]
    return missing_products_ids
# dodatkowe wyjasnienie:     # odwolujemy sie do product.product.id bo interesuje nas podstawowy id Product a nie id produktu u tego uzytkownika - dlatego, ze id produktów pochodnych są rozne i niezalezne od Product a przez to niemozliwe do porownywania

def generate_shopping_list(request: Any) -> Set[int]:
    """
    Get list of missing_products_ids and combines it with products added to shopping list by user. Returns set of ids"""
    user = request.user
    missing_products_ids = get_missing_products(user)
    shopping_list_items = ShoppingListProduct.objects.filter(user=user).values_list('product', flat=True)
    items_to_buy = [*missing_products_ids,*shopping_list_items]
    return set(items_to_buy)

def create_product_from_ids(products_ids: List[int], user) -> List[ShoppingListProduct]:
    """
    Create list of ShoppingListProducts from list of Product ids.
    """
    products = []
    for i in products_ids:
        # product, created = ShoppingListProduct.objects.filter(user=user).get_or_create(defaults=['product', i])
        product, created = ShoppingListProduct.objects.get_or_create(
            user=user,
            # defaults=['product', i])
            product = i,
            defaults={'quantity': 1})
        products.append(product)
    return products # to lista ids czy obiektów?

@login_required
def shopping_list(request):
    products = ShoppingListProduct.objects.filter(user=request.user)
    if request.method == 'POST':
        form = GenerateShoppingListActivate(request.POST)
        if form.is_valid():
            generate_shopping_list_activated = form.cleaned_data['generate_shopping_list_activated']
            if generate_shopping_list_activated:
                messages.success(request, "Shopping list generated")
                products_ids = generate_shopping_list(request) # add handling of empty set in template
                created_products = create_product_from_ids(products_ids, request.user) 
                if created_products:
                    products = ShoppingListProduct.objects.filter(user=request.user) # ponownie pobieram z bazy

            else:
                messages.error(request, "Shopping list could not be generated")

        # return redirect(request, 'shopping_list', context={'products': products}) 
        return redirect('shopping_list')  
    else:
        form = GenerateShoppingListActivate()
        return render(request, 'shopping_list/shopping_list.html', context={
            'products': products,
            'form': form})

def add_by_aggregating_product(product, user):
    """Checks if product id in the fridge. 
    If yes - increase the quantity of the product and return True,
    if not - returns Flse. """
    
    querry_set = ShoppingListProduct.objects.filter(
        user=user, 
        product__name=product.product.name, 
        )
    if querry_set.exists():
        quantity = product.quantity
        # querry_set.update(quantity= F('quantity') +1) # zle dziala, bo zwieksza o 1 a nie o dodana ilosc
        querry_set.update(quantity=F('quantity') + quantity)
        return True
    else:
        return False

@login_required
def add_product_to_shopping_list(request):
    if request.method == 'POST':
        # czyszcze messages:
        message_storage = messages.get_messages(request)
        for message in message_storage:
            pass
        # to czysci stare messages
        form = AddShoppingProductForm(request.POST)
        if form.is_valid():
            # Użyj form.save() - nie twórz produktu ręcznie
            shopping_list_product = form.save(commit=False) # tutaj z Meta(w form) jest tworony ShoppingListProduct
            shopping_list_product.user = request.user
            updated = add_by_aggregating_product(shopping_list_product, request.user)
            if not updated:
                shopping_list_product.save()
            
            messages.success(request, 'Product added to shopping list.')

            is_default = form.cleaned_data['add_to_default']
            if is_default:
                default_product, created = DefaultShoppingProduct.objects.get_or_create(
                    user=request.user,
                    product=shopping_list_product.product
                )
                if created:
                    messages.success(request, 'Product added to default shopping products')

            # return render(request, 'add_product_to_shopping_list.html', 
                        # context={'form': form, 'shopping_list_product': shopping_list_product})
            return redirect('shopping_list')
        else:
            messages.error(request, 'Error - check your input.')
            
    else:
        form = AddShoppingProductForm()
    
    return render(request, 'add_product_to_shopping_list.html', context={'form': form})


def generate_shopping_list(request):
    pass

