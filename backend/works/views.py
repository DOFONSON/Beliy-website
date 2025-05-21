from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.views.generic.detail import DetailView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import models
from .models import Product, Author, ProductAuthor, Article, Rating, Place, LiteraryWork, User, UserProfile, Comment, Cart, CartItem
from .forms import ProductForm, AuthorForm, ProductAuthorForm
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from rest_framework import viewsets, status, generics
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny, IsAuthenticated
from rest_framework.decorators import action, api_view, permission_classes, parser_classes
from rest_framework.response import Response
from .serializers import (
    ArticleSerializer, ProductSerializer, AuthorSerializer,
    PlaceSerializer, LiteraryWorkSerializer, CommentSerializer, UserSerializer, UserProfileSerializer, CartSerializer, CartItemSerializer
)
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
import logging
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from django.db.models import Avg, Count, Sum, F, ExpressionWrapper, DecimalField

logger = logging.getLogger(__name__)

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

@login_required
@require_POST
def rate_article(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    rating_value = request.POST.get('rating')
    print(request)
    if not rating_value or not rating_value.isdigit():
        return JsonResponse({'error': 'Неверное значение оценки'}, status=400)
    
    rating_value = int(rating_value)
    if not 1 <= rating_value <= 5:
        return JsonResponse({'error': 'Оценка должна быть от 1 до 5'}, status=400)
    
    rating, created = Rating.objects.update_or_create(
        content_type=ContentType.objects.get_for_model(Article),
        object_id=article.id,
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

    def get_object(self):
        """
        Retrieve object by slug or id
        """
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        value = self.kwargs[lookup_url_kwarg]

        # Try to get by ID first
        if value.isdigit():
            self.lookup_field = 'id'
            self.kwargs[self.lookup_field] = int(value)
        else:
            self.lookup_field = 'slug'
            self.kwargs[self.lookup_field] = value

        return super().get_object()

    @action(detail=True, methods=['post'])
    def comments(self, request, slug=None):
        article = self.get_object()
        
        if not request.user.is_authenticated:
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
            
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(
                user=request.user,
                content_type=ContentType.objects.get_for_model(Article),
                object_id=article.id
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def rate(self, request, slug=None):
        article = self.get_object()
        
        if not request.user.is_authenticated:
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
            
        rating_value = request.data.get('rating')
        
        try:
            rating_value = float(rating_value)
            if not 1 <= rating_value <= 5:
                raise ValueError()
        except (TypeError, ValueError):
            return Response({'error': 'Rating must be between 1 and 5'}, status=status.HTTP_400_BAD_REQUEST)
        
        rating, _ = Rating.objects.update_or_create(
            content_type=ContentType.objects.get_for_model(Article),
            object_id=article.id,
            user=request.user,
            defaults={'value': rating_value}
        )
        
        return Response({
            'success': True,
            'average_rating': article.get_average_rating,
            'rating_count': article.ratings.count()
        })

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().order_by('-created_at')
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = Product.objects.all()
        
        # Example 1: Basic aggregation - count ratings and calculate average
        queryset = queryset.annotate(
            total_ratings=Count('ratings'),
            avg_rating=Avg('ratings__value'),
            total_comments=Count('comments')
        )
        
        # Example 2: Complex aggregation - calculate total revenue per product
        queryset = queryset.annotate(
            total_revenue=ExpressionWrapper(
                F('price') * Count('cartitem'),
                output_field=DecimalField()
            )
        )
        
        # Example 3: Conditional aggregation - count high ratings (4-5 stars)
        queryset = queryset.annotate(
            high_ratings_count=Count(
                'ratings',
                filter=models.Q(ratings__value__gte=4)
            )
        )
        
        return queryset

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

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    try:
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response(
                {'error': 'Пожалуйста, укажите имя пользователя и пароль'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(username=username, password=password)

        if user is not None:
            # Создаем профиль пользователя, если его нет
            UserProfile.objects.get_or_create(user=user)
            
            refresh = RefreshToken.for_user(user)
            serializer = UserSerializer(user, context={'request': request})
            
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': serializer.data
            })
        else:
            return Response(
                {'error': 'Неверное имя пользователя или пароль'},
                status=status.HTTP_401_UNAUTHORIZED
            )
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return Response(
            {'error': 'Произошла ошибка при входе'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')
    first_name = request.data.get('first_name', '')
    last_name = request.data.get('last_name', '')

    if not username or not email or not password:
        return Response(
            {'message': 'Пожалуйста, заполните все обязательные поля'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if User.objects.filter(username=username).exists():
        return Response(
            {'message': 'Пользователь с таким именем уже существует'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if User.objects.filter(email=email).exists():
        return Response(
            {'message': 'Пользователь с таким email уже существует'},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = User.objects.create_user(
        username=username,
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name
    )

    # Создаем профиль пользователя
    UserProfile.objects.create(user=user)

    refresh = RefreshToken.for_user(user)
    serializer = UserSerializer(user, context={'request': request})
    
    return Response({
        'access': str(refresh.access_token),
        'refresh': str(refresh),
        'user': serializer.data
    }, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_auth(request):
    return Response({
        'authenticated': True,
        'user': UserSerializer(request.user).data
    })

@api_view(['GET', 'PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def profile_view(request):
    user = request.user
    if request.method == 'GET':
        serializer = UserSerializer(user, context={'request': request})
        return Response(serializer.data)
    elif request.method in ['PUT', 'PATCH']:
        # Обновляем данные пользователя
        user_serializer = UserSerializer(user, data=request.data, partial=(request.method == 'PATCH'), context={'request': request})
        if user_serializer.is_valid():
            user_serializer.save()
            
            # Обновляем профиль пользователя
            profile, created = UserProfile.objects.get_or_create(user=user)
            profile_serializer = UserProfileSerializer(profile, data=request.data, partial=(request.method == 'PATCH'))
            if profile_serializer.is_valid():
                profile_serializer.save()
            
            # Возвращаем обновленные данные пользователя с контекстом запроса
            return Response(UserSerializer(user, context={'request': request}).data)
        return Response(user_serializer.errors, status=400)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_comment(request, comment_id):
    try:
        comment = Comment.objects.get(id=comment_id)
    except Comment.DoesNotExist:
        return Response({'error': 'Comment not found'}, status=status.HTTP_404_NOT_FOUND)

    if not request.user.is_superuser:
        return Response(
            {'error': 'You do not have permission to delete this comment'},
            status=status.HTTP_403_FORBIDDEN
        )

    comment.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

class CartView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CartSerializer

    def get_object(self):
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        return cart

class AddToCartView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CartItemSerializer

    def create(self, request, *args, **kwargs):
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))

        if not product_id:
            return Response(
                {'error': 'Product ID is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        product = get_object_or_404(Product, id=product_id)
        cart, _ = Cart.objects.get_or_create(user=request.user)

        # Проверяем, есть ли уже такой товар в корзине
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )

        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        serializer = self.get_serializer(cart_item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class CartItemView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CartItemSerializer
    lookup_field = 'id'
    lookup_url_kwarg = 'item_id'

    def get_queryset(self):
        return CartItem.objects.filter(cart__user=self.request.user)

class ProductRatingView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        product_id = kwargs.get('product_id')
        rating_value = request.data.get('rating')

        if not rating_value:
            return Response(
                {'error': 'Rating value is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        product = get_object_or_404(Product, id=product_id)
        
        # Создаем или обновляем рейтинг
        rating, created = product.ratings.get_or_create(
            user=request.user,
            defaults={'value': rating_value}
        )

        if not created:
            rating.value = rating_value
            rating.save()

        # Обновляем средний рейтинг продукта
        product.update_average_rating()

        return Response({
            'average_rating': product.average_rating
        }, status=status.HTTP_201_CREATED)
