from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import os
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Avg, Count
from django.urls import reverse
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from io import BytesIO

def user_avatar_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f'user_{instance.id}_{int(timezone.now().timestamp())}.{ext}'
    return os.path.join('avatars', filename)

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название")
    slug = models.SlugField(max_length=100, unique=True, verbose_name="Slug")
    description = models.TextField(blank=True, verbose_name="Описание")
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children', verbose_name="Родительская категория")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

# 1. Пользователь (расширяем стандартную модель)
class User(AbstractUser):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    avatar = models.ImageField(upload_to=user_avatar_path, null=True, blank=True)
    
    @property
    def cart(self):
        return self.carts.filter(is_active=True).first()

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.username

    def get_short_name(self):
        return self.first_name or self.username

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
    @property
    def get_average_rating(self):
        from django.db.models import Avg
        return self.ratings.aggregate(average=Avg('value'))['average'] or 0
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    image = models.ImageField(upload_to='articles/', null=True, blank=True)
    content = models.TextField(blank=True)
    
    ratings = GenericRelation(Rating)
    comments = GenericRelation(Comment)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = ('Статья')
        verbose_name_plural = ('Статьи')
        ordering = ['-created_at', 'title']
    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('article-detail', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

# 5. Товар
class ProductManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_available=True)
    
    def active(self):
        return self.get_queryset()
    
    def with_high_ratings(self):
        return self.get_queryset().filter(average_rating__gte=4.0)
    
    def recently_added(self):
        return self.get_queryset().order_by('-created_at')[:5]
    
    def with_comments(self):
        return self.get_queryset().annotate(
            comment_count=models.Count('comments')
        ).filter(comment_count__gt=0)

STATUS_CHOICES = [
    ('active', 'Активный'),
    ('archived', 'В архиве'),
    ('out_of_stock', 'Нет в наличии'),
    ('draft', 'Черновик'),
]

class Product(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название")
    description = models.TextField(verbose_name="Описание")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    image = models.ImageField(upload_to='products/', null=True, blank=True, verbose_name="Изображение")
    pdf_file = models.FileField(upload_to='product_pdfs/', null=True, blank=True, verbose_name="PDF документ")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products', verbose_name="Категория")
    authors = models.ManyToManyField('Author', through='ProductAuthor', related_name='authored_products', verbose_name="Авторы")
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0, verbose_name="Средний рейтинг")
    quantity = models.PositiveIntegerField(default=0, verbose_name="Количество")
    is_available = models.BooleanField(default=True, verbose_name="Доступен")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name="Статус")

    objects = ProductManager()

    ratings = GenericRelation(Rating)
    comments = GenericRelation(Comment)
    class Meta:
                verbose_name = ('Товар')
                verbose_name_plural = ('Товары')
    def __str__(self):
        return self.title

    def update_average_rating(self):
        avg = self.ratings.aggregate(Avg('value'))['value__avg']
        self.average_rating = avg if avg is not None else 0
        self.save()

    def get_absolute_url(self):
        return reverse('product-detail', kwargs={'pk': self.pk})

    def generate_pdf(self):
        """Генерирует PDF документ для продукта"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        # Создаем стили
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30
        )

        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=20
        )

        text_style = ParagraphStyle(
            'CustomText',
            parent=styles['Normal'],
            fontSize=12,
            spaceAfter=12
        )

        # Добавляем заголовок
        story.append(Paragraph(f"Информация о продукте: {self.title}", title_style))
        story.append(Spacer(1, 20))

        # Добавляем изображение, если оно есть
        if self.image:
            try:
                img = Image(self.image.path, width=400, height=300)
                story.append(img)
                story.append(Spacer(1, 20))
            except:
                pass

        # Основная информация
        story.append(Paragraph("Основная информация:", subtitle_style))
        story.append(Paragraph(f"Описание: {self.description}", text_style))
        story.append(Paragraph(f"Цена: {self.price} ₽", text_style))
        story.append(Paragraph(f"Категория: {self.category}", text_style))
        story.append(Paragraph(f"Статус: {self.status}", text_style))
        story.append(Paragraph(f"Количество: {self.quantity}", text_style))
        story.append(Spacer(1, 20))

        # Информация об авторах
        if self.authors.exists():
            story.append(Paragraph("Авторы:", subtitle_style))
            for author in self.authors.all():
                story.append(Paragraph(f"• {author.name}", text_style))
            story.append(Spacer(1, 20))

        # Рейтинги и комментарии
        story.append(Paragraph("Рейтинг и отзывы:", subtitle_style))
        story.append(Paragraph(f"Средний рейтинг: {self.average_rating}", text_style))
        
        # Добавляем последние комментарии
        comments = self.comments.all().order_by('-created_at')[:5]
        if comments:
            story.append(Paragraph("Последние комментарии:", text_style))
            for comment in comments:
                story.append(Paragraph(f"• {comment.user.username}: {comment.text}", text_style))
        
        story.append(Spacer(1, 20))

        # Добавляем даты
        story.append(Paragraph("Даты:", subtitle_style))
        story.append(Paragraph(f"Создан: {self.created_at.strftime('%d.%m.%Y %H:%M')}", text_style))
        story.append(Paragraph(f"Обновлен: {self.updated_at.strftime('%d.%m.%Y %H:%M')}", text_style))

        # Создаем PDF
        doc.build(story)
        buffer.seek(0)
        return buffer

    def save_pdf(self):
        """Сохраняет сгенерированный PDF в поле pdf_file"""
        if not self.pdf_file:
            pdf_buffer = self.generate_pdf()
            filename = f'product_{self.id}_{int(timezone.now().timestamp())}.pdf'
            self.pdf_file.save(filename, pdf_buffer, save=True)

    def get_pdf_response(self):
        """Возвращает HTTP ответ с PDF файлом"""
        pdf_buffer = self.generate_pdf()
        response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="product_{self.id}.pdf"'
        return response

# 6. Корзина
class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='carts')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Корзина пользователя {self.user.username}"

    def get_total_price(self):
        return sum(item.get_total_price() for item in self.items.all())

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'

# 7. Элемент корзины
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.quantity} x {self.product.title}"

    def get_total_price(self):
        return self.product.price * self.quantity

    class Meta:
        verbose_name = 'Товар в корзине'
        verbose_name_plural = 'Товары в корзине'
        unique_together = ('cart', 'product')

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
    name = models.CharField(max_length=200, verbose_name="Имя")
    bio = models.TextField(blank=True, verbose_name="Биография")
    photo = models.ImageField(upload_to='authors/', null=True, blank=True, verbose_name="Фото")
    products = models.ManyToManyField(
        'Product',
        through='ProductAuthor',
        through_fields=('author', 'product'),
        related_name='product_authors',
        verbose_name="Товары"
    )

    class Meta:
        verbose_name = 'Автор'
        verbose_name_plural = 'Авторы'

    def __str__(self):
        return self.name

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s profile"

    class Meta:
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профили пользователей'