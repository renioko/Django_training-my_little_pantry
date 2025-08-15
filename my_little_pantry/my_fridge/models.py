from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

# Create your models here.
class Product(models.Model):
    name = models.CharField(max_length=100)
    unit = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.name} - unit: {self.unit}"
    
    def save(self, *args, **kwargs):
        if self.name:
            self.name = self.name.strip().lower()
        super().save(*args, **kwargs)    

    
class FridgeProduct(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    expiry_date = models.DateField()
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} - {self.quantity} {self.product.unit}"
    
    def show_expiry_date(self):
        return f"{self.product.name} - expires on {self.expiry_date}"
    
    def is_fresh(self):
        """
        Returns True if products is not expired, otherwise False.
        """
        todays_date = timezone.now().date()
        return todays_date <= self.expiry_date
    
    def is_default_product(self):
        return DefaultProduct.objects.filter(
            user=self.user,
            product=self.product
        ).exists()
    

class DefaultProduct(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.product.name} (default product)"
