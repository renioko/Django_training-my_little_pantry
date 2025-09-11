from django import forms

from .models import ShoppingListProduct, DefaultShoppingProduct
from my_fridge.models import Product

class AddShoppingProductForm(forms.ModelForm):
    product = forms.CharField(max_length=50, label="Product name")  # Zmień nazwę z product_name
    quantity = forms.IntegerField(max_value=1000, min_value=0, required=True)
    unit = forms.ChoiceField(
        choices=[
            ('szt','szt'), ('L', 'L'), ('ml', 'ml'),
            ('kg', 'kg'), ('g', 'g'), ('loaf', 'loaf'),
        ], 
        label='Unit'
    )
    is_important = forms.BooleanField(
        required=False, 
        label="Important! Don't forget to buy this one!"
    )
    add_to_default = forms.BooleanField(
        required=False,
        label='Add to default product'
    )

    class Meta:
        model = ShoppingListProduct
        fields = ['product', 'quantity', 'is_important']  # Dodaj product z powrotem

    def clean(self):
        cleaned_data = super().clean()
        name_input = cleaned_data.get('product')
        unit_input = cleaned_data.get('unit')

        if name_input and unit_input:
            name = name_input.strip().lower()
            product, created = Product.objects.get_or_create(name=name, defaults={'unit': unit_input})
            cleaned_data['product'] = product # tutaj do slownika cleaned_data jest przekazany obiekt

        return cleaned_data

class GenerateShoppingListActivate(forms.Form):
        # nowa rzecz 
    generate_shopping_list_activated = forms.BooleanField(
        required=False,
        label='Generate Shopping list'
    )

class RemoveShoppingList(forms.Form):
    products = forms.ModelMultipleChoiceField(
        queryset=ShoppingListProduct.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label='Shopping products to remove'
    )
    
