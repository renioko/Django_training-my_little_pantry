from django.db.models import Sum, F
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import FridgeProductForm
from .models import Product, FridgeProduct, DefaultProduct

# Create your views here.

def index(request):
    context = {'': ""}
    return render(request, 'my_fridge/index.html', context)


@login_required
def fridge_view(request):
    products = FridgeProduct.objects.filter(user=request.user).order_by('expiry_date')
    return render(request, 'my_fridge/fridge.html', {'products': products})


def aggregate_product(product, user):
    fridge_products_quantity = (
        FridgeProduct.objects.filter(
            user=user, product__name = product.product.name, expiry_date=product.expiry_date
            ).aggregate(total=Sum('quantity'))['total'] or 0
    )
# rozwlekle:
    # result = FridgeProduct.objects.aggregate(total=Sum('quantity'))
    # total = result['total']
    # if total is None:
    #     total = 0
    return fridge_products_quantity

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
        querry_set.update(quantity= F('quantity') +1)
        return True
    else:
        return False
        
    
@login_required
def add_fridge_product(request):
    if request.method == 'POST':
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
            messages.success(request, "Product added or updated")

            return redirect('fridge')
        else:
            messages.error(request, "Form error - check your input")
    else:
        form = FridgeProductForm()
    return render(request, 'my_fridge/add_fridge_product.html', {'form': form})

@login_required
def remmove_fridge_product(request):
    if request.method == 'POST':
        form = FridgeProductForm(request.POST)
        if form.is_valid():
            fridge_item = form.save(commit=False)
            fridge_item.user = request.user

            FridgeProduct.delete(keep_parents=True)

            fridge_item.save()

        


@login_required
def shopping_list(request):
    default_products = DefaultProduct.objects.filter(user=request.user)
    fridge_item = FridgeProduct.objects.filter(user=request.user)
    fridge_product_ids = fridge_item.values_list('product_id', flat=True) #co to oznacza

    missing_products = default_products.exclude(product_id__in=fridge_product_ids)

    return render(request, 'my_fridge/shopping_list.html', {
        'missing_products': missing_products
    })





