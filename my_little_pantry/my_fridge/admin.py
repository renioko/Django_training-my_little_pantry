from django.contrib import admin
from .models import Product, DefaultProduct, FridgeProduct

admin.site.register(Product)
admin.site.register(DefaultProduct)
admin.site.register(FridgeProduct)

# Register your models here.
