from django import forms
from django.forms import inlineformset_factory
from .models import Product, Author, ProductAuthor

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['title', 'price', 'image', 'description', 'category', 'status', 'stock_date']
        widgets = {
            'stock_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

# Создаем формсет для авторов
ProductAuthorFormSet = inlineformset_factory(
    Product, ProductAuthor,
    fields=['author', 'role'],
    extra=1,
    can_delete=True
) 