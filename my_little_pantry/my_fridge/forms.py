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

    def clean(self):
        cleaned_data = super().clean()
        name_input = cleaned_data.get('product')
        unit_input = cleaned_data.get('unit')

        if name_input and unit_input:
            name = name_input.strip().lower()
        product, created = Product.objects.get_or_create(name=name, defaults={'unit': unit_input})
        cleaned_data['product'] = product # przypisuje spowrotem

        return cleaned_data

        
class DeleteFridgeProduct(forms.Form):
    removed_product = forms.ChoiceField(label='Product to remove')
    quantity = forms.IntegerField(max_value=1000, min_value=0, required=True)

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # dynamicznie tworzymy choices tylko dla produktów tego użytkownika - odqolujemy sie do zmiennej removed_product, pod polem w formie, ktore tworzymy powyzej. teraz uzypełniamy je o konkretny wybór
        self.fields['removed_product'].choices=[(item.id, f"{item.product.name} - {item.quantity} {item.product.unit}") for item in FridgeProduct.objects.filter(user=user)]


# jesli bym tak zostawila to serwer zaladuje tylko raz, a pozniej uzytkownicy moga cos dodac i to sie juz by nie zaladowało. dlatego trzeba byłododac __init__ jak powyzej
    # removed_product = forms.ChoiceField(choices=((item.id, item.product.name) for item in FridgeProduct.objects.all()), label='Product to remove')
    # quantity = forms.IntegerField(max_value=1000, min_value=0, required=True)

class ExpiredProductsChecker(forms.Form):
    check_for_expired = forms.BooleanField(
        required=False,
        label='Check for expired products')
