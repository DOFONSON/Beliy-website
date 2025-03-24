from django.urls import path
from .views import ProductListView, get_product_statistics

urlpatterns = [
    path('products/', ProductListView.as_view(), name='product-list'),
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
    path('statistics/', get_product_statistics, name='product-statistics'),
] 