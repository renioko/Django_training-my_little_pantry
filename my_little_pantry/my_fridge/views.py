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

@login_required
def add_fridge_product(request):
    if request.method == 'POST':
        form = FridgeProductForm(request.POST)
        if form.is_valid():
            fridge_item = form.save(commit=False)
            fridge_item.user = request.user
            fridge_item.save()

        # if checkbox 'add to default product':
            if form.cleaned_data['add_to_default']:
                DefaultProduct.objects.get_or_create(
                    user=request.user,
                    product=fridge_item.product
                )
            messages.success(request, "Product added")

            return redirect('fridge')
        else:
            messages.error(request, "Error filling the form. Enter correct data")
    else:
        form = FridgeProductForm()
    return render(request, 'my_fridge/add_fridge_product.html', {'form': form})

@login_required
def shopping_list(request):
    default_products = DefaultProduct.objects.filter(user=request.user)
    fridge_item = FridgeProduct.objects.filter(user=request.user)
    fridge_product_ids = fridge_item.values_list('product_id', flat=True) #co to oznacza

    missing_products = default_products.exclude(product_id__in=fridge_product_ids)

    return render(request, 'my_fridge/shopping_list.html', {
        'missing_products': missing_products
    })






