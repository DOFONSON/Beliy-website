from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import (
    ProductListView, ProductDetailView, 
    ProductCreateView, ProductUpdateView, ProductDeleteView,
    rate_article, login_view, register_view, profile_view, check_auth,
    CartView, AddToCartView, CartItemView, ExamListAPIView
)

router = DefaultRouter()
router.register(r'articles', views.ArticleViewSet)
router.register(r'products', views.ProductViewSet)
router.register(r'authors', views.AuthorViewSet)
router.register(r'places', views.PlaceViewSet)
router.register(r'literary-works', views.LiteraryWorkViewSet)
router.register(r'users', views.UserViewSet)

api_urlpatterns = [
    path('', include(router.urls)),
    path('auth/login/', login_view, name='login'),
    path('auth/register/', register_view, name='register'),
    path('auth/profile/', profile_view, name='profile'),
    path('auth/check/', check_auth, name='check-auth'),
    path('comments/<int:comment_id>/delete/', views.delete_comment, name='delete-comment'),
    path('cart/', CartView.as_view(), name='cart'),
    path('cart/add/', AddToCartView.as_view(), name='add-to-cart'),
    path('cart/items/<int:item_id>/', CartItemView.as_view(), name='cart-item'),
    path('products/<int:product_id>/rate/', views.ProductRatingView.as_view(), name='product_rate'),
    path('exam-list/', ExamListAPIView.as_view(), name='exam-list-api'),
]

urlpatterns = [
    path('api/', include(api_urlpatterns)),
    path('products/', ProductListView.as_view(), name='product-list'),
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
    path('products/create/', ProductCreateView.as_view(), name='product-create'),
    path('products/<int:pk>/update/', ProductUpdateView.as_view(), name='product-update'),
    path('products/<int:pk>/delete/', ProductDeleteView.as_view(), name='product-delete'),
    path('articles/<int:article_id>/rate/', rate_article, name='rate-article'),
    path('exam/', views.exam_view, name='exam-list'),
] 