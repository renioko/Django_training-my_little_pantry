from django import forms
from .models import Product, DefaultProduct, FridgeProduct

class FridgeProductForm(forms.ModelForm):
    add_to_default = forms.BooleanField(
        required=False,
        label="Add to default products",
    )

    class Meta:
        model = FridgeProduct
        fields = ['product', 'quantity', 'expiry_date', 'add_to_default']
        widgets = {
            'expiry_date': forms.DateInput(attrs={'type': 'date'}),
            }