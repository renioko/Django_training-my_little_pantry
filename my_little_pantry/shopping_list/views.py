from django.db.models import Sum, F
from django.shortcuts import render, redirect

from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .forms import AddShoppingProductForm
from my_fridge.models import Product, DefaultProduct
from .models import ShoppingListProduct, DefaultShoppingProduct
from my_fridge.views import index

# Create your views here.

# def index()

@login_required
def shopping_list(request):
    products = ShoppingListProduct.objects.filter(user=request.user)
    return render(request, 'shopping_list/shopping_list.html', context={'products': products})

# @login_required
# def add_product_to_shopping_list(request):
#     if request.method == 'POST':
#         form = AddShoppingProductForm(request.POST)
#         if not form.is_valid():
#             messages.error(request, 'Error - check your input.')
#             return render(request, 'add_product_to_shopping_list.html', context={'form':form})
#         else:
#             product_name = form.cleaned_data['product'] # nie robie strip lower bo juz clean() to robi
#             unit = form.cleaned_data['unit']
#             product, created = Product.objects.get_or_create(name=product_name, defaults={'unit':unit})
#             if created:
#                 messages.success(request, 'Product created.')

#             shopping_list_product = ShoppingListProduct(
#                 user=request.user,
#                 product=product,
#                 quantity=form.cleaned_data['quantity'],
#                 unit=form.cleaned_data['unit'],
#                 is_important=form.cleaned_data['is_important']
#             )
#             shopping_list_product.save()
#             messages.success(request, 'Product added to shopping list.')

#             is_default = form.cleaned_data['add_to_default']
#             if is_default:
#                 default_product, created = DefaultShoppingProduct.objects.get_or_create(
#                     user=request.user,
#                     product=form.cleaned_data['product']
#                 )
#                 if created:
#                     messages.success(request, 'Product added to default shopping products')

#         return render(
#             request,
#             'add_product_to_shopping_list.html', 
#             context={'form':form, 'shopping_list_product':shopping_list_product}
#             )
#     else:
#         form = AddShoppingProductForm()
#         return render(request, 'add_product_to_shopping_list.html', context={'form': form})

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
            # shopping_list_product.unit = form.cleaned_data['unit']  # Dodaj unit z formularza - nie trzeba, jest dodany do Product, a ProductShoppingList go nie uzywa
            # nowa czesc - aggregating products:
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

