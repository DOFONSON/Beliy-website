from django import forms
from django.forms import inlineformset_factory
from .models import Product, Author, ProductAuthor

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['title', 'price', 'image', 'description']

class AuthorForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = ['name', 'bio', 'photo']

class ProductAuthorForm(forms.ModelForm):
    class Meta:
        model = ProductAuthor
        fields = ['author', 'role']

# Создаем формсет для авторов
ProductAuthorFormSet = inlineformset_factory(
    Product, ProductAuthor,
    fields=['author', 'role'],
    extra=1,
    can_delete=True
) 