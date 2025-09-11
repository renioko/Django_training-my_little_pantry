from django.db.models import Sum, F
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import FridgeProductForm, DeleteFridgeProduct, ExpiredProductsChecker, DeleteFridgeProductList, RemoveDefaultProducts
from .models import Product, FridgeProduct, DefaultProduct

# Create your views here.

def index(request):
    return render(request, 'my_fridge/index.html', {})


@login_required
def fridge_view(request):
    """
    Shows the list of available products in the fridge.
    """
    fridge_products = FridgeProduct.objects.filter(user=request.user).order_by('expiry_date')
    default_products = DefaultProduct.objects.filter(user=request.user)

    return render(request, 'my_fridge/fridge.html', {
        'fridge_products': fridge_products, 
        'default_products': default_products,
        })

@login_required
def check_expired_view(request):
    """
    Shows the list of expired products and asks for a confirmation to delete them.
    """
    fridge_products = FridgeProduct.objects.filter(user=request.user) 
    expired_products = [p for p in fridge_products if not p.is_fresh] # is fresh juz nie jest metodą, tylko atrybutem (przez property)
    if expired_products:
        return render(request, 'my_fridge/expired.html', {
            "expired_products": expired_products
        })
    else:
        messages.error(request, 'No expired products to remove')
        return redirect('fridge')

@login_required
def remove_expired_fridge_products(request):
    """
    Removes all expired products from the fridge after receiving a confirmation.
    """
    fridge_products = FridgeProduct.objects.filter(user=request.user)
    if request.method == 'POST':
        expired_products = [p for p in fridge_products if not p.is_fresh]
        if expired_products:
            for ep in expired_products:
                ep.delete()
            messages.success(request, "Expired products removed successfully.")
        else:
            messages.error(request, "No expired products found.")
        return redirect('fridge')

def add_by_aggregating_product(product, user):
    """Checks if product id in the fridge. 
    If yes - increase the quantity of the product and return True,
    if not - returns Flse. """
    
    querry_set = FridgeProduct.objects.filter(
        user=user, 
        product__name=product.product.name, 
        expiry_date = product.expiry_date
        )
    if querry_set.exists():
        quantity = product.quantity
        querry_set.update(quantity= F('quantity') + quantity)
        return True
    else:
        return False
        
@login_required
def add_fridge_product(request):
    if request.method == 'POST':
        messages_storage = messages.get_messages(request)
        for message in messages_storage:
            pass
        # to zuzywa stare messages

        form = FridgeProductForm(request.POST)
        if form.is_valid():
            fridge_item = form.save(commit=False)
            fridge_item.user = request.user
            updated = add_by_aggregating_product(fridge_item, fridge_item.user)
            if not updated:
                form.save()

        # if checkbox 'add to default product':
            if form.cleaned_data['add_to_default']:
                DefaultProduct.objects.get_or_create(
                    user=request.user,
                    product=fridge_item.product
                )
                messages.success(request, 'Product added to default fridge product')
            messages.success(request, "Product added or updated")
            return redirect('fridge')
        else:
            messages.error(request, "Form error - check your input")
    else:
        form = FridgeProductForm()
    return render(request, 'my_fridge/add_fridge_product.html', {'form': form})

@login_required
def remove_fridge_product(request):
    if request.method == 'POST':
        delete_form = DeleteFridgeProduct(request.user, request.POST or None)

        if delete_form.is_valid():
            user = request.user
            removed_product_quantity = delete_form.cleaned_data['quantity']
            product_id = delete_form.cleaned_data['removed_product']


            fridge_item = FridgeProduct.objects.filter(user=user, id=product_id)
            if not fridge_item.exists():
                messages.error(request,'Product not found.')
                return redirect('fridge')
            # but it should if it is on the list
            else:
                fridge_item_quantity = fridge_item.values_list('quantity', flat=True)[0]

                remaining_quantity = fridge_item_quantity - removed_product_quantity

                if remaining_quantity > 0:
                    fridge_item.update(quantity=remaining_quantity)
                else:
                    fridge_item.delete()
        
                messages.success(request, "Product updated or removed")
                return redirect('fridge')
            
    else:
        form = DeleteFridgeProduct(request.user)
        return render(request, 'my_fridge/remove_fridge_product.html', context={'form': form})

@login_required
def remove_fridge_product_list(request):
    fridge_products = FridgeProduct.objects.filter(user=request.user)
    if request.method == 'POST':
        to_delete_list = request.POST.getlist('to_delete') 
        to_delete_list = [int(i) for i in to_delete_list if i.isdigit()]

        FridgeProduct.objects.filter(user=request.user, id__in=to_delete_list).delete()
        messages.success(request, "products deleted.")

        return redirect('fridge')
    return render(request, 'my_fridge/remove_list_products.html', {'fridge_products': fridge_products} )

    #  ====
@login_required
def remove_products_checkboxes_form(request):
    if request.method == 'POST':
        form = DeleteFridgeProductList(request.POST)
        form.fields['products'].queryset = FridgeProduct.objects.filter(user=request.user)

        if form.is_valid():
            products_to_delete = form.cleaned_data['products']
            count = products_to_delete.count()
            products_to_delete.delete()
            messages.success(request, f"{count} products deleted successfully")
            return redirect('fridge')
    else:
        form = DeleteFridgeProductList()
        form.fields['products'].queryset = FridgeProduct.objects.filter(user=request.user)
    return render(request, 'my_fridge/remove_products_form.html', {'form': form })

@login_required
def remove_defaults(request):
    if request.method == 'POST':
        form = RemoveDefaultProducts(request.POST)
        form.fields['products'].queryset = DefaultProduct.objects.filter(user=request.user)
        # powyżej podmieniam wartosci wywołane w form - tam jest wywolana ogolnie klasa, bez konkretnych produktów. tutaj ustawiam, że chodzi o DEfaultProducts tego uzytkownika - odwoluje sie do pola 'products' i atrybutu queryset, ktorego wynik podmieniam na produkty uzytkownika

        if form.is_valid():
            products_to_delete = form.cleaned_data['products']
            # tu powyzej pobieram juz odpowiednio podstawione dane z pola products
            product_names = [str(p.product.name) for p in products_to_delete]
            products_to_delete.delete()
            message = 'Products removed:'+ ', '.join(product_names)
            messages.success(request, message)

    # na poczatku, póki nie ma 'post' wyswietlam na stronie po prostu liste produktów
    else:
        form = RemoveDefaultProducts()
        form.fields['products'].queryset = DefaultProduct.objects.filter(user=request.user)
    return render(request, "my_fridge/defaults.html", {'form': form})


