# works/models.py
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.urls import reverse
from django.db.models import Manager, Avg, Count, Q
from datetime import timedelta

# 1. Пользователь (расширяем стандартную модель)
class User(AbstractUser):
    email = models.EmailField(unique=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    
    @property
    def cart(self):
        return self.carts.filter(is_active=True).first()

# 2. Оценка (общая для всех сущностей)
class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    value = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)])
    
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    class Meta:
                verbose_name = ('Оценка')
                verbose_name_plural = ('Оценки')
    created_at = models.DateTimeField(default=timezone.now)

# 3. Комментарий (общий для всех сущностей)
class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField(max_length=2000)
    
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    class Meta:
            verbose_name = ('Комментарий')
            verbose_name_plural = ('Комментарии')
    created_at = models.DateTimeField(default=timezone.now)

# 4. Статья
class Article(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)  # Добавлено поле
    image = models.ImageField(upload_to='articles/')
    content = models.TextField()
    
    ratings = GenericRelation(Rating)
    comments = GenericRelation(Comment)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
            verbose_name = ('Статья')
            verbose_name_plural = ('Статьи')
    def __str__(self):
        return self.title

# Собственный менеджер для товаров
class ProductManager(Manager):
    def get_discounted(self):
        """Получить товары со скидкой (старше 30 дней)"""
        month_ago = timezone.now() - timedelta(days=30)
        return self.filter(created_at__lte=month_ago)
    
    def get_popular(self):
        """Получить популярные товары (с высоким рейтингом)"""
        return self.annotate(
            avg_rating=Avg('ratings__value'),
            reviews_count=Count('comments')
        ).filter(avg_rating__gte=4.0)

# 5. Товар
class Product(models.Model):
    CATEGORY_CHOICES = [
        ('BOOK', 'Книга'),
        ('SOUVENIR', 'Сувенир'),
        ('ARTWORK', 'Арт-объект'),
    ]
    
    STATUS_CHOICES = [
        ('IN_STOCK', 'В наличии'),
        ('OUT_OF_STOCK', 'Нет в наличии'),
        ('COMING_SOON', 'Скоро в продаже'),
    ]

    title = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/')
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='BOOK')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='IN_STOCK')
    created_at = models.DateTimeField(default=timezone.now)
    last_modified = models.DateTimeField(auto_now=True)
    stock_date = models.DateTimeField(help_text="Дата поступления на склад")
    
    ratings = GenericRelation(Rating)
    comments = GenericRelation(Comment)
    
    objects = ProductManager()

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ['-created_at', 'title']

    def __str__(self):
        return f"{self.title} - {self.price}₽"

    def get_absolute_url(self):
        return reverse('product-detail', kwargs={'pk': self.pk})

    def get_discount_percentage(self):
        """Расчет скидки в зависимости от времени хранения"""
        days_in_stock = (timezone.now() - self.stock_date).days
        if days_in_stock > 90:  # Более 3 месяцев
            return 30
        elif days_in_stock > 60:  # Более 2 месяцев
            return 20
        elif days_in_stock > 30:  # Более 1 месяца
            return 10
        return 0

# 6. Корзина
class Cart(models.Model):
    user = models.ForeignKey(User, related_name='carts', on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    class Meta:
                verbose_name = ('Корзина')
                verbose_name_plural = ('Корзины')
    @property
    def total(self):
        return sum(item.subtotal for item in self.items.all())

# 7. Элемент корзины
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
                verbose_name = ('Элемент корзины')
                verbose_name_plural = ('Элементы корзины')
    @property
    def subtotal(self):
        return self.product.price * self.quantity

# 8. Место
class Place(models.Model):
    title = models.CharField(max_length=200)
    address = models.CharField(max_length=500)
    description = models.TextField()
    
    ratings = GenericRelation(Rating)
    comments = GenericRelation(Comment)
    class Meta:
                verbose_name = ('Место')
                verbose_name_plural = ('Места')
    def __str__(self):
        return self.title

# 9. Произведение
class LiteraryWork(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    image = models.ImageField(upload_to='works/')
    
    ratings = GenericRelation(Rating)
    comments = GenericRelation(Comment)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
                verbose_name = ('Произведение')
                verbose_name_plural = ('Произведения')
    def __str__(self):
        return self.title

# Новая модель для акций
class Promotion(models.Model):
    PROMOTION_TYPES = [
        ('DISCOUNT', 'Скидка'),
        ('SPECIAL', 'Специальное предложение'),
        ('BUNDLE', 'Комплект'),
    ]

    title = models.CharField(max_length=200)
    type = models.CharField(max_length=20, choices=PROMOTION_TYPES)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField()
    products = models.ManyToManyField(Product, related_name='promotions')
    
    class Meta:
        ordering = ['-start_date']

    def is_active(self):
        now = timezone.now()
        return self.start_date <= now <= self.end_date