from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.views.generic.detail import DetailView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Product, Author, ProductAuthor, Article, ArticleRating, Place, LiteraryWork
from .forms import ProductForm, AuthorForm
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.decorators import action
from rest_framework.response import Response
from .serializers import (
    ArticleSerializer, ProductSerializer, AuthorSerializer,
    PlaceSerializer, LiteraryWorkSerializer, CommentSerializer
)

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

from django import forms

class AuthorForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = ['name', 'bio', 'photo']

class ProductAuthorForm(forms.ModelForm):
    class Meta:
        model = ProductAuthor
        fields = ['author', 'role']


@login_required
@require_POST
def rate_article(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    rating_value = request.POST.get('rating')
    
    if not rating_value or not rating_value.isdigit():
        return JsonResponse({'error': 'Неверное значение оценки'}, status=400)
    
    rating_value = int(rating_value)
    if not 1 <= rating_value <= 5:
        return JsonResponse({'error': 'Оценка должна быть от 1 до 5'}, status=400)
    
    rating, created = ArticleRating.objects.update_or_create(
        article=article,
        user=request.user,
        defaults={'value': rating_value}
    )
    
    return JsonResponse({
        'success': True,
        'average_rating': article.get_average_rating(),
        'rating_count': article.get_rating_count()
    })

class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.all().order_by('-created_at')
    serializer_class = ArticleSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().order_by('-created_at')
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class PlaceViewSet(viewsets.ModelViewSet):
    queryset = Place.objects.all()
    serializer_class = PlaceSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class LiteraryWorkViewSet(viewsets.ModelViewSet):
    queryset = LiteraryWork.objects.all().order_by('-created_at')
    serializer_class = LiteraryWorkSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    @action(detail=True, methods=['post'])
    def rate(self, request, pk=None):
        work = self.get_object()
        rating_value = request.data.get('rating')
        
        if not rating_value or not isinstance(rating_value, int) or not 1 <= rating_value <= 5:
            return Response({'error': 'Invalid rating value'}, status=400)
        
        rating, _ = work.ratings.update_or_create(
            user=request.user,
            defaults={'value': rating_value}
        )
        
        return Response({
            'success': True,
            'average_rating': work.get_average_rating()
        })
