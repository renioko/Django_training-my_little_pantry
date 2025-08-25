from django import forms

from .models import ShoppingListProduct, DefaultShoppingProduct
from my_fridge.models import Product

# class AddShoppingProductForm(forms.ModelForm):
#     product_name = forms.CharField(max_length=50, label="Product name")
#     quantity = forms.IntegerField(
#         max_value=1000, min_value=0, required=True
#     )
#     unit = forms.ChoiceField(
#         choices=[
#         ('szt','szt'), 
#         ('L', 'L'),
#         ('ml', 'ml'),
#         ('kg', 'kg'),
#         ('g', 'g'),
#         ('loaf', 'loaf'),
#         ], 
#         label='Unit'
#     )
#     is_important = forms.BooleanField(
#         required=False, 
#         label="Important! Don't forget to buy this one!"
#     )
#     add_to_default = forms.BooleanField(
#         required=False,
#         label='Add to default product'
#     )

#     class Meta:
#         model = ShoppingListProduct
#         fields = []
#         # fields = ['quantity', 'is_important' ] # bez unit bo nie ma go w modelu
#         # field_order = ['product_name', 'quantity', 'unit', 'is_important', 'add_to_default']
#     # trzeba podmienic 'product' ktory jest ForeignKey zeby zawieral tylko name a nie byl FK:
#     def clean(self):
#         cleaned_data = super().clean()
#         product_name_input = cleaned_data.get('product_name')
#         unit_input = cleaned_data.get('unit')

#         if product_name_input and unit_input:
#             # mozna nie robic strip() i lower() bo robi to model Product
#             product_name_input = product_name_input.strip().lower()
#             product, created = Product.objects.get_or_create(
#                 name=product_name_input, 
#                 defaults={'unit':unit_input}
#                 )
#             cleaned_data['product'] = product

#         return cleaned_data
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