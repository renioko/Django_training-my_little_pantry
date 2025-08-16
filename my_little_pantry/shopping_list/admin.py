from django.contrib import admin
from .models import ShoppingListProduct, DefaultShoppingProduct


# Register your models here.
admin.register(ShoppingListProduct)
admin.register(DefaultShoppingProduct)

@admin.register(ShoppingListProduct)
class ShoppingProductAdmin(admin.ModelAdmin):
    list_display = ['user', 'product_name', 'quantity', 'product_unit', 'is_important']
    list_filter = ['user', 'product']
    search_fields = ['user__username', 'product__name']

    def product_name(self, obj):
        return obj.product.name
    product_name.short_description = 'Product name'

    def product_unit(self, obj):
        return obj.product.unit
    product_unit.short_description = 'Unit'


@admin.register(DefaultShoppingProduct)
class DefaultShoppingProductAdmin(admin.ModelAdmin):
    list_display = ['user', 'product']