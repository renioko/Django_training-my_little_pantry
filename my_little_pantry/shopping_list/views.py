from django.db.models import Sum, F
from django.shortcuts import render, redirect

from django.contrib import messages
from django.contrib.auth.decorators import login_required

from shopping_list.forms import AddShoppingProductForm, GenerateShoppingListActivate, RemoveShoppingList, RemoveDefaultShopping
from my_fridge.models import Product, DefaultProduct
from .models import ShoppingListProduct, DefaultShoppingProduct
from my_fridge.models import DefaultProduct, FridgeProduct
from my_fridge.views import index
from typing import List, Any, Set

# Create your views here.

# def index()

# 🚩 nie dodawane są default products do shopping list, chociaz sama lista sie wyswietla 
# 3. po usunieciu z lodówki produkt powinien sie generowac w shopping list


def get_missing_products(user: Any) -> List[int]:
    """
    Checks if all DefaultProducts are in the FRIDGE (FridgeProduct).
    Returns list of missing products as Product ids.
    """
    default_fridge_products = DefaultProduct.objects.filter(user=user)
    # values_list odwoluje sie do 'product'FK czyli do Product. dlatego nie uzywam 'id' tylko 'product' poniżej:
    products_in_fridge = FridgeProduct.objects.filter(user=user).values_list('product', flat=True)
    missing_products_ids = [product.product.id for product in default_fridge_products if product.product.id not in products_in_fridge]
    return missing_products_ids
# dodatkowe wyjasnienie:     # odwolujemy sie do product.product.id bo interesuje nas podstawowy id Product a nie id produktu u tego uzytkownika - dlatego, ze id produktów pochodnych są rozne i niezalezne od Product a przez to niemozliwe do porownywania

def get_default_products(user) -> Set[int]:
    """
    Join default shopping products and default fridge products.
    Returns set of default products ids.
    """
    default_shopping_products_ids = DefaultShoppingProduct.objects.filter(user=user).values_list('product', flat=True)
    default_fridge_products_ids = DefaultProduct.objects.filter(user=user).values_list('product', flat=True)
    all_default_products_ids = set([*default_fridge_products_ids, *default_shopping_products_ids])
    return all_default_products_ids

def generate_shopping_list(request: Any) -> Set[int]:
    """
    Get list of missing_products_ids and combines it with products added to shopping list by user. Returns set of all products to buy ids"""
    user = request.user

    # all default product lists:
    default_product_ids = get_default_products(user)

    # products missing from the fridge
    missing_products_ids = get_missing_products(user)
    # ids of products that needs to be bought
    products_to_buy_from_defaults_and_fridge = set([*missing_products_ids, *default_product_ids])

    # products already in shopping list
    shopping_list_ids = set(ShoppingListProduct.objects.filter(user=user).values_list('product', flat=True))

    # ids to buy without those already added to the list:
    ids_to_add_to_list = products_to_buy_from_defaults_and_fridge.difference(shopping_list_ids)

    return (ids_to_add_to_list)

def create_product_from_ids(products_ids: List[int], user) -> List[ShoppingListProduct]:
    """
    Create list of ShoppingListProducts from list of Product ids.
    """
    shopping_products = []
    for i in products_ids:
        # product, created = ShoppingListProduct.objects.filter(user=user).get_or_create(defaults=['product', i])
        shopping_product = ShoppingListProduct.objects.create(
            user=user,
            product = Product.objects.get(pk=i) #foreign key do Product - bez tego wywolania mam bład: Cannot assign "4": "ShoppingListProduct.product" must be a "Product" instance.""
            # product=i # to wywalało blad, bo musi byc Product instance
            )
        shopping_products.append(shopping_product)
        print(f'shopping list products: {shopping_products}')
    return shopping_products # to lista ids czy obiektów?


# gotowa wygenerowana lista ma zastepowac tą co juz istnieje
@login_required
def shopping_list(request):
    products = ShoppingListProduct.objects.filter(user=request.user)
    if request.method == 'POST':
        form = GenerateShoppingListActivate(request.POST)
        if form.is_valid():
            generate_shopping_list_activated = form.cleaned_data['generate_shopping_list_activated'] # raczej nie bedzie wcale potrzebne

            if generate_shopping_list_activated: # to tez
                # messages.success(request, "Shopping list generated")
                products_ids = generate_shopping_list(request) # add handling of empty set in template

                # 🚩❗tutaj trzeba wykasowac te produkty co juz sa i stworzyc nowe:
                if products_ids:    # 🛠️
                    # products.delete()   # 🛠️
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
    
    shopping_products = ShoppingListProduct.objects.filter(
        user=user, 
        product__name=product.product.name, 
        )
    if shopping_products.exists():
        quantity = product.quantity
        # querry_set.update(quantity= F('quantity') +1) # zle dziala, bo zwieksza o 1 a nie o dodana ilosc
        shopping_products.update(quantity=F('quantity') + quantity)
        return True
    else:
        return False

@login_required
def add_product_to_shopping_list(request):
    if request.method == 'POST':
        form = AddShoppingProductForm(request.POST)
        if form.is_valid():
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
            return redirect('shopping_list')
        else:
            messages.error(request, 'Error - check your input.')
            
    else:
        form = AddShoppingProductForm()
    
    return render(request, 'add_product_to_shopping_list.html', context={'form': form})

@login_required
def remove_shopping_products(request):
    if request.method == 'POST':
        form = RemoveShoppingList(request.POST)
        form.fields['products'].queryset = ShoppingListProduct.objects.filter(user=request.user)

        if form.is_valid():
            products_to_remove = form.cleaned_data['products']
            product_names = set([str(p.product.name) for p in products_to_remove])
            products_to_remove.delete()
            message = 'Products removed: ' + ', '.join(product_names)
            messages.success(request, message)
    else:
        form = RemoveShoppingList()
        form.fields['products'].queryset = ShoppingListProduct.objects.filter(user=request.user)
    return render(request, 'shopping_list/remove_shopping_products.html', {'form': form})

@login_required
def remove_default(request):
    if request.method == "POST":
        form = RemoveDefaultShopping(request.POST)
        form.fields['products'].queryset = DefaultShoppingProduct.objects.filter(user=request.user)

        if form.is_valid():
            products_to_remove = form.cleaned_data['products']
            product_names = set([str(p.product.name) for p in products_to_remove])
            products_to_remove.delete()
            message = "Removed products: " + ", ".join(product_names)
            messages.success(request, message)

    else:
        form = RemoveDefaultShopping()
        form.fields['products'].queryset = DefaultShoppingProduct.objects.filter(user=request.user)
    return render(request, 'shopping_list/remove_default.html', {'form': form})

@login_required
def remove_all(request):
    products = ShoppingListProduct.objects.filter(user=request.user)
    if request.method == 'POST':
        try:
            products.delete()
            messages.success(request, 'Shopping list emptied successfully.')
        except Exception as e:
            messages.error(request, f'Error while emptying shopping  list: {e}')
        return redirect('shopping_list')

    return render(request, 'shopping_list/shopping_list.html', {'products': products})


