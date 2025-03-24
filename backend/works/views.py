from django.shortcuts import render
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.views.generic.detail import DetailView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Product, Author, ProductAuthor
from .forms import ProductForm, AuthorForm

# Create your views here.

class ProductListView(ListView):
    model = Product
    template_name = 'works/product_list.html'
    context_object_name = 'products'

    def get_queryset(self):
        # Используем select_related для оптимизации запросов
        return Product.objects.select_related('category').prefetch_related(
            'authors',
            'comments__user',
            'ratings'
        ).all()

class ProductDetailView(DetailView):
    model = Product
    template_name = 'works/product_detail.html'

    def get_queryset(self):
        # Оптимизируем запросы для детального просмотра
        return Product.objects.select_related('category').prefetch_related(
            'authors__productauthor_set',  # Загружаем информацию о ролях авторов
            'comments__user',
            'ratings__user'
        )

class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'works/product_form.html'
    success_url = reverse_lazy('product-list')

class ProductUpdateView(LoginRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'works/product_form.html'
    
    def get_success_url(self):
        return reverse_lazy('product-detail', kwargs={'pk': self.object.pk})

class ProductDeleteView(LoginRequiredMixin, DeleteView):
    model = Product
    template_name = 'works/product_confirm_delete.html'
    success_url = reverse_lazy('product-list')

# Создадим формы для работы с авторами
from django import forms

class AuthorForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = ['name', 'bio', 'photo']

class ProductAuthorForm(forms.ModelForm):
    class Meta:
        model = ProductAuthor
        fields = ['author', 'role']

# Создадим шаблоны для работы с формами
