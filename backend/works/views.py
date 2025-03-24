from django.shortcuts import render
from django.views.generic import ListView, DetailView
from django.db.models import Avg, Count, Sum, Q
from django.utils import timezone
from datetime import timedelta
from .models import Product, Promotion

# Create your views here.

class ProductListView(ListView):
    model = Product
    template_name = 'works/product_list.html'
    
    def get_queryset(self):
        queryset = Product.objects.all()
        
        # Пример использования filter()
        if self.request.GET.get('category'):
            queryset = queryset.filter(category=self.request.GET['category'])
        
        # Пример использования exclude()
        queryset = queryset.exclude(status='OUT_OF_STOCK')
        
        # Пример использования order_by()
        queryset = queryset.order_by('-created_at')
        
        # Пример использования __ для связанных таблиц
        queryset = queryset.filter(
            promotions__start_date__lte=timezone.now(),
            promotions__end_date__gte=timezone.now()
        )
        
        # Пример аннотации
        queryset = queryset.annotate(
            avg_rating=Avg('ratings__value'),
            comment_count=Count('comments'),
            total_sales=Sum('cartitem__quantity')
        )
        
        # Пример фильтрации по аннотированному полю
        if self.request.GET.get('min_rating'):
            queryset = queryset.filter(avg_rating__gte=float(self.request.GET['min_rating']))
        
        return queryset

def get_product_statistics(request):
    # Пример использования агрегации
    stats = Product.objects.aggregate(
        total_products=Count('id'),
        average_price=Avg('price'),
        total_comments=Count('comments')
    )
    
    # Пример использования related_name
    user = request.user
    user_cart_items = user.cart.items.all()  # используем related_name='items'
    
    # Пример использования Q объектов
    discounted_products = Product.objects.filter(
        Q(promotions__isnull=False) | 
        Q(created_at__lte=timezone.now() - timedelta(days=30))
    )
    
    # Пример использования собственного менеджера
    popular_products = Product.objects.get_popular()
    
    return render(request, 'works/statistics.html', {
        'stats': stats,
        'cart_items': user_cart_items,
        'discounted_products': discounted_products,
        'popular_products': popular_products
    })
