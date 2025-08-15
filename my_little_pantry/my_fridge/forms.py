from django import forms
from .models import Product, DefaultProduct, FridgeProduct

class FridgeProductForm(forms.ModelForm):
    add_to_default = forms.BooleanField(
        required=False,
        label="Add to default products",
    )
    product = forms.CharField(max_length=20)
    unit = forms.ChoiceField(
        choices=[
        ('szt','szt'), 
        ('L', 'L'),
        ('ml', 'ml'),
        ('kg', 'kg'),
        ('g', 'g'),
        ('loaf', 'loaf'),
        ], 
        label='Unit'
        )

    class Meta:
        model = FridgeProduct
        fields = ['product', 'quantity', 'unit', 'expiry_date', 'add_to_default']
        widgets = {
            'expiry_date': forms.DateInput(attrs={'type': 'date'}),
            }
        
    # def clean_product(self):
    #     product = self.cleaned_data['product']
    #     name = product.strip().lower()
    #     unit = self.cleaned_data['unit']
    #     product, create = Product.objects.get_or_create(
    #         name=name,
    #         defaults={'unit': unit}

    #     )
    #     return product

    def clean(self):
        cleaned_data = super().clean()
        name_input = cleaned_data.get('product')
        unit_input = cleaned_data.get('unit')

        if name_input and unit_input:
            name = name_input.strip().lower()
        product, created = Product.objects.get_or_create(name=name, defaults={'unit': unit_input})
        cleaned_data['product'] = product # przypisuje spowrotem

        return cleaned_data

        
