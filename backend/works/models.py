# works/models.py
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

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

# 5. Товар
class Product(models.Model):
    title = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/')
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)  # Добавлено поле

    ratings = GenericRelation(Rating)
    comments = GenericRelation(Comment)
    class Meta:
                verbose_name = ('Товар')
                verbose_name_plural = ('Товары')
    def __str__(self):
        return self.title

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

# Добавляем новую промежуточную модель для связи Product и Author
class ProductAuthor(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    author = models.ForeignKey('Author', on_delete=models.CASCADE)
    role = models.CharField(max_length=50, choices=[
        ('AUTHOR', 'Автор'),
        ('ILLUSTRATOR', 'Иллюстратор'),
        ('TRANSLATOR', 'Переводчик'),
    ])
    added_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ['product', 'author', 'role']
        verbose_name = 'Автор продукта'
        verbose_name_plural = 'Авторы продуктов'

class Author(models.Model):
    name = models.CharField(max_length=200)
    bio = models.TextField()
    photo = models.ImageField(upload_to='authors/', null=True, blank=True)
    products = models.ManyToManyField(
        'Product',
        through='ProductAuthor',
        through_fields=('author', 'product'),
        related_name='authors'
    )

    class Meta:
        verbose_name = 'Автор'
        verbose_name_plural = 'Авторы'

    def __str__(self):
        return self.name