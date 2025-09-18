from django.db import models
from django.utils import timezone

from my_fridge.models import Product

from django.contrib.auth.models import User
# Create your models here.

class ShoppingListProduct(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1) # albo float
    is_important = models.BooleanField(default=False)
    # default

    def __str__(self):
        if self.is_important:
            is_important = '!'
        else:
            is_important = ''

        return f"{self.product.name} - {self.quantity} {self.product.unit} {is_important}"


    def is_default_shopping_product(self):
        """Checks if product is exist as Default product."""
        return DefaultShoppingProduct.objects.filter(
            user=self.user,
            product=self.product
        ).exists()


class DefaultShoppingProduct(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.product.name}"