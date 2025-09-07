from django.db.models import Sum, F
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import FridgeProductForm, DeleteFridgeProduct, ExpiredProductsChecker
from .models import Product, FridgeProduct, DefaultProduct

# Create your views here.

def index(request):
    return render(request, 'my_fridge/index.html', {})


@login_required
def fridge_view(request):
    products = FridgeProduct.objects.filter(user=request.user).order_by('expiry_date')
    default_products = DefaultProduct.objects.filter(user=request.user)
    # if request.method == 'POST': # czy zrobic z tego oddzielny view?
    #     # form = ExpiredProductsChecker(request.POST)
    #     # if form.is_valid():
    #         # check_expired_activated = form.cleaned_data['check_for_expired']
    #         # if check_expired_activated:
    #     messages.success(request, 'Checked for expired products.')
    #     fresh_products = [p for p in products if p.is_fresh()] # do usuniecia
    #     expired_products = [p for p in products if not p.is_fresh()] # do usuniecia
    #     return render(request, 'my_fridge/expired.html', {  # do usuniecia
    #         'fresh_products': fresh_products, # do usuniecia
    #         'expired_products': expired_products # do usuniecia
    #     }) # do usuniecia

    return render(request, 'my_fridge/fridge.html', {
        'products': products, 
        'default_products': default_products,
        # 'form': form
        })

# @login_required
# def check_expired_view(request):
#     products = FridgeProduct.objects.filter(user=request.user)
#     if request.method =='POPT':   
#         form = ExpiredProductsChecker(request.POST)
#         if form.is_valid():
#             check_expired_activated = form.cleaned_data['check_for_expired']
#             if check_expired_activated:
#                 messages.success(request, 'Checked for expired products.')
#                 fresh_products = [p for p in products if p.is_fresh()]
#                 expired_products = [p for p in products if not p.is_fresh()]
#         return render(request, 'my_fridge/expired.html', {
#             'fresh_products': fresh_products,
#             'expired_products': expired_products
#         })

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





# def aggregate_product(product, user):
#     fridge_products_quantity = (
#         FridgeProduct.objects.filter(
#             user=user, product__name = product.product.name, expiry_date=product.expiry_date
#             ).aggregate(total=Sum('quantity'))['total'] or 0
#     )
# # rozwlekle:
#     # result = FridgeProduct.objects.aggregate(total=Sum('quantity'))
#     # total = result['total']
#     # if total is None:
#     #     total = 0
#     return fridge_products_quantity