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
from typing import Optional, List, Dict, Any, Union, Tuple
from django.conf import settings

def user_avatar_path(instance: 'User', filename: str) -> str:
    """
    Генерирует путь для сохранения аватара пользователя.
    
    Args:
        instance: Экземпляр модели User
        filename: Имя загруженного файла
        
    Returns:
        str: Путь для сохранения файла
    """
    ext = filename.split('.')[-1]
    filename = f'user_{instance.id}_{int(timezone.now().timestamp())}.{ext}'
    return os.path.join('avatars', filename)

class Category(models.Model):
    """
    Модель категории для организации контента.
    
    Attributes:
        name: Название категории
        slug: URL-friendly версия названия
        description: Описание категории
        parent: Родительская категория (для создания иерархии)
        created_at: Дата создания
        updated_at: Дата последнего обновления
    """
    name = models.CharField(max_length=100, verbose_name="Название")
    slug = models.SlugField(max_length=100, unique=True, verbose_name="Slug")
    description = models.TextField(blank=True, verbose_name="Описание")
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, 
                             related_name='children', verbose_name="Родительская категория")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ['name']

    def __str__(self) -> str:
        """Возвращает строковое представление категории."""
        return self.name

    def save(self, *args: Any, **kwargs: Any) -> None:
        """
        Сохраняет категорию, генерируя slug если он не указан.
        
        Args:
            *args: Позиционные аргументы
            **kwargs: Именованные аргументы
        """
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

# 1. Пользователь (расширяем стандартную модель)
class User(AbstractUser):
    """
    Расширенная модель пользователя.
    
    Attributes:
        email: Email пользователя (уникальный)
        first_name: Имя пользователя
        last_name: Фамилия пользователя
        avatar: Аватар пользователя
    """
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    avatar = models.ImageField(upload_to=user_avatar_path, null=True, blank=True)
    
    @property
    def cart(self) -> Optional['Cart']:
        """
        Возвращает активную корзину пользователя.
        
        Returns:
            Optional[Cart]: Активная корзина или None, если корзина не найдена
        """
        return self.carts.filter(is_active=True).first()

    def get_full_name(self) -> str:
        """
        Возвращает полное имя пользователя.
        
        Returns:
            str: Полное имя или username, если имя не указано
        """
        return f"{self.first_name} {self.last_name}".strip() or self.username

    def get_short_name(self) -> str:
        """
        Возвращает короткое имя пользователя.
        
        Returns:
            str: Имя или username, если имя не указано
        """
        return self.first_name or self.username

class Rating(models.Model):
    """
    Модель для хранения оценок пользователей.
    
    Attributes:
        user: Пользователь, поставивший оценку
        value: Значение оценки (1-5)
        content_type: Тип контента, к которому относится оценка
        object_id: ID объекта, к которому относится оценка
        content_object: Связь с объектом, к которому относится оценка
        created_at: Дата создания оценки
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    value = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)])
    
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = 'Оценка'
        verbose_name_plural = 'Оценки'

class Comment(models.Model):
    """
    Модель для хранения комментариев пользователей.
    
    Attributes:
        user: Пользователь, оставивший комментарий
        text: Текст комментария
        content_type: Тип контента, к которому относится комментарий
        object_id: ID объекта, к которому относится комментарий
        content_object: Связь с объектом, к которому относится комментарий
        created_at: Дата создания комментария
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField(max_length=2000)
    
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

class Article(models.Model):
    """
    Модель статьи.
    
    Attributes:
        title: Заголовок статьи
        slug: URL-friendly версия заголовка
        image: Изображение статьи
        content: Содержимое статьи
        source_url: URL источника статьи
        ratings: Связь с оценками
        comments: Связь с комментариями
        created_at: Дата создания
        updated_at: Дата последнего обновления
    """
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    image = models.ImageField(upload_to='articles/', null=True, blank=True)
    content = models.TextField(blank=True)
    source_url = models.URLField(verbose_name="URL источника", null=True, blank=True)
    
    ratings = GenericRelation(Rating)
    comments = GenericRelation(Comment)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Статья'
        verbose_name_plural = 'Статьи'
        ordering = ['-created_at', 'title']

    def __str__(self) -> str:
        """Возвращает строковое представление статьи."""
        return self.title

    def get_absolute_url(self) -> str:
        """
        Возвращает абсолютный URL статьи.
        
        Returns:
            str: URL статьи
        """
        return reverse('article-detail', kwargs={'slug': self.slug})

    def save(self, *args: Any, **kwargs: Any) -> None:
        """
        Сохраняет статью, генерируя slug если он не указан.
        
        Args:
            *args: Позиционные аргументы
            **kwargs: Именованные аргументы
        """
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    @property
    def get_average_rating(self) -> float:
        """
        Возвращает средний рейтинг статьи.
        
        Returns:
            float: Средний рейтинг или 0, если оценок нет
        """
        return self.ratings.aggregate(average=Avg('value'))['average'] or 0

    @classmethod
    def search_by_content(cls, query: str) -> models.QuerySet:
        """
        Поиск статей по содержимому.
        
        Args:
            query: Поисковый запрос
            
        Returns:
            QuerySet: Найденные статьи
        """
        return cls.objects.filter(content__icontains=query)

    @classmethod
    def get_recent_articles_info(cls) -> List[Dict[str, Any]]:
        """
        Получение информации о последних статьях.
        
        Returns:
            List[Dict[str, Any]]: Список словарей с информацией о статьях
        """
        return list(cls.objects.order_by('-created_at')[:5].values('title', 'created_at'))

    @classmethod
    def get_article_slugs(cls) -> List[str]:
        """
        Получение списка slug'ов статей.
        
        Returns:
            List[str]: Список slug'ов
        """
        return list(cls.objects.values_list('slug', flat=True))

    @classmethod
    def count_articles_with_comments(cls) -> int:
        """
        Подсчет статей с комментариями.
        
        Returns:
            int: Количество статей с комментариями
        """
        return cls.objects.filter(comments__isnull=False).distinct().count()

    @classmethod
    def check_article_exists(cls, slug: str) -> bool:
        """
        Проверка существования статьи.
        
        Args:
            slug: Slug статьи
            
        Returns:
            bool: True если статья существует, False в противном случае
        """
        return cls.objects.filter(slug=slug).exists()

    @classmethod
    def update_article_slugs(cls) -> None:
        """Обновляет slug'и для всех статей без slug'а."""
        articles = cls.objects.all()
        for article in articles:
            if not article.slug:
                article.slug = slugify(article.title)
                article.save()

    @classmethod
    def delete_old_articles(cls, days: int = 30) -> Tuple[int, Dict[str, int]]:
        """
        Удаляет старые статьи.
        
        Args:
            days: Количество дней, после которых статья считается старой
            
        Returns:
            Tuple[int, Dict[str, int]]: Количество удаленных статей и словарь с деталями удаления
        """
        old_date = timezone.now() - timezone.timedelta(days=days)
        return cls.objects.filter(created_at__lt=old_date).delete()

# 5. Товар
class ProductManager(models.Manager):
    """
    Менеджер для работы с продуктами.
    
    Предоставляет методы для фильтрации и получения продуктов с различными условиями.
    """
    
    def get_queryset(self) -> models.QuerySet:
        """
        Возвращает базовый QuerySet с фильтрацией по доступности.
        
        Returns:
            QuerySet: QuerySet с доступными продуктами
        """
        return super().get_queryset().filter(is_available=True)
    
    def active(self) -> models.QuerySet:
        """
        Возвращает активные продукты.
        
        Returns:
            QuerySet: QuerySet с активными продуктами
        """
        return self.get_queryset()
    
    def with_high_ratings(self) -> models.QuerySet:
        """
        Возвращает продукты с высоким рейтингом (>= 4.0).
        
        Returns:
            QuerySet: QuerySet с продуктами с высоким рейтингом
        """
        return self.get_queryset().filter(average_rating__gte=4.0)
    
    def recently_added(self) -> models.QuerySet:
        """
        Возвращает последние добавленные продукты.
        
        Returns:
            QuerySet: QuerySet с последними 5 добавленными продуктами
        """
        return self.get_queryset().order_by('-created_at')[:5]
    
    def with_comments(self) -> models.QuerySet:
        """
        Возвращает продукты с комментариями.
        
        Returns:
            QuerySet: QuerySet с продуктами, имеющими комментарии
        """
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
    """
    Модель продукта.
    
    Attributes:
        title: Название продукта
        description: Описание продукта
        price: Цена продукта
        image: Изображение продукта
        pdf_file: PDF документ продукта
        website_url: URL сайта продукта
        created_at: Дата создания
        updated_at: Дата последнего обновления
        category: Категория продукта
        authors: Авторы продукта
        average_rating: Средний рейтинг
        quantity: Количество на складе
        is_available: Доступность продукта
        status: Статус продукта
    """
    title = models.CharField(max_length=200, verbose_name="Название")
    description = models.TextField(verbose_name="Описание")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    image = models.ImageField(upload_to='products/', null=True, blank=True, verbose_name="Изображение")
    pdf_file = models.FileField(upload_to='product_pdfs/', null=True, blank=True, verbose_name="PDF документ")
    website_url = models.URLField(verbose_name="URL сайта", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, 
                               related_name='products', verbose_name="Категория")
    authors = models.ManyToManyField('Author', through='ProductAuthor', 
                                   related_name='authored_products', verbose_name="Авторы")
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0, 
                                       verbose_name="Средний рейтинг")
    quantity = models.PositiveIntegerField(default=0, verbose_name="Количество")
    is_available = models.BooleanField(default=True, verbose_name="Доступен")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', 
                            verbose_name="Статус")

    objects = ProductManager()

    ratings = GenericRelation(Rating)
    comments = GenericRelation(Comment)

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

    def __str__(self) -> str:
        """Возвращает строковое представление продукта."""
        return self.title

    def update_average_rating(self) -> None:
        """Обновляет средний рейтинг продукта."""
        self.average_rating = self.ratings.aggregate(avg=models.Avg('value'))['avg'] or 0
        self.save()

    def get_absolute_url(self) -> str:
        """
        Возвращает абсолютный URL продукта.
        
        Returns:
            str: URL продукта
        """
        return reverse('product-detail', kwargs={'pk': self.pk})

    def generate_pdf(self) -> BytesIO:
        """
        Генерирует PDF документ для продукта.
        
        Returns:
            BytesIO: Буфер с PDF документом
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []

        # Заголовок
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30
        )
        elements.append(Paragraph(self.title, title_style))

        # Описание
        elements.append(Paragraph("Описание:", styles['Heading2']))
        elements.append(Paragraph(self.description, styles['Normal']))
        elements.append(Spacer(1, 20))

        # Цена
        elements.append(Paragraph(f"Цена: {self.price}", styles['Normal']))
        elements.append(Spacer(1, 20))

        # Изображение
        if self.image:
            img = Image(self.image.path, width=400, height=300)
            elements.append(img)
            elements.append(Spacer(1, 20))

        # Авторы
        if self.authors.exists():
            elements.append(Paragraph("Авторы:", styles['Heading2']))
            for author in self.authors.all():
                elements.append(Paragraph(f"- {author.name}", styles['Normal']))
            elements.append(Spacer(1, 20))

        doc.build(elements)
        buffer.seek(0)
        return buffer

    def save_pdf(self) -> None:
        """Сохраняет сгенерированный PDF документ."""
        if not self.pdf_file:
            pdf_buffer = self.generate_pdf()
            filename = f'product_{self.id}_{int(timezone.now().timestamp())}.pdf'
            self.pdf_file.save(filename, ContentFile(pdf_buffer.getvalue()))

    def get_pdf_response(self) -> HttpResponse:
        """
        Возвращает HTTP ответ с PDF документом.
        
        Returns:
            HttpResponse: Ответ с PDF документом
        """
        pdf_buffer = self.generate_pdf()
        response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="product_{self.id}.pdf"'
        return response

    @classmethod
    def search_by_title(cls, query: str) -> models.QuerySet:
        """
        Поиск продуктов по названию.
        
        Args:
            query: Поисковый запрос
            
        Returns:
            QuerySet: Найденные продукты
        """
        return cls.objects.filter(title__icontains=query)

    @classmethod
    def search_by_description(cls, query: str) -> models.QuerySet:
        """
        Поиск продуктов по описанию.
        
        Args:
            query: Поисковый запрос
            
        Returns:
            QuerySet: Найденные продукты
        """
        return cls.objects.filter(description__icontains=query)

    @classmethod
    def get_active_products_info(cls) -> List[Dict[str, Any]]:
        """
        Получение информации об активных продуктах.
        
        Returns:
            List[Dict[str, Any]]: Список словарей с информацией о продуктах
        """
        return list(cls.objects.filter(is_available=True).values('title', 'price', 'quantity'))

    @classmethod
    def get_product_titles(cls) -> List[str]:
        """
        Получение списка названий продуктов.
        
        Returns:
            List[str]: Список названий
        """
        return list(cls.objects.values_list('title', flat=True))

    @classmethod
    def count_available_products(cls) -> int:
        """
        Подсчет доступных продуктов.
        
        Returns:
            int: Количество доступных продуктов
        """
        return cls.objects.filter(is_available=True).count()

    @classmethod
    def check_product_exists(cls, title: str) -> bool:
        """
        Проверка существования продукта.
        
        Args:
            title: Название продукта
            
        Returns:
            bool: True если продукт существует, False в противном случае
        """
        return cls.objects.filter(title=title).exists()

    @classmethod
    def mark_out_of_stock(cls, product_ids: List[int]) -> int:
        """
        Помечает продукты как отсутствующие на складе.
        
        Args:
            product_ids: Список ID продуктов
            
        Returns:
            int: Количество обновленных продуктов
        """
        return cls.objects.filter(id__in=product_ids).update(
            is_available=False,
            status='out_of_stock'
        )

    @classmethod
    def delete_draft_products(cls) -> Tuple[int, Dict[str, int]]:
        """
        Удаляет черновики продуктов.
        
        Returns:
            Tuple[int, Dict[str, int]]: Количество удаленных продуктов и словарь с деталями удаления
        """
        return cls.objects.filter(status='draft').delete()

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

class Resource(models.Model):
    name = models.CharField(max_length=200, verbose_name="Название")
    url = models.URLField(verbose_name="URL ресурса")
    description = models.TextField(verbose_name="Описание")
    tags = models.CharField(max_length=500, verbose_name="Теги", help_text="Теги через запятую")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Ресурс"
        verbose_name_plural = "Ресурсы"
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    @classmethod
    def search_by_description(cls, query):
        return cls.objects.filter(description__icontains=query)

    @classmethod
    def search_by_tags(cls, tag):
        return cls.objects.filter(tags__contains=tag)

    @classmethod
    def get_active_resources(cls):
        return cls.objects.filter(is_active=True).values('name', 'url')

    @classmethod
    def get_resource_names(cls):
        return cls.objects.values_list('name', flat=True)

    @classmethod
    def count_active_resources(cls):
        return cls.objects.filter(is_active=True).count()

    @classmethod
    def check_resource_exists(cls, name):
        return cls.objects.filter(name=name).exists()

    @classmethod
    def deactivate_old_resources(cls, days=30):
        from django.utils import timezone
        from datetime import timedelta
        old_date = timezone.now() - timedelta(days=days)
        return cls.objects.filter(created_at__lt=old_date).update(is_active=False)

    @classmethod
    def delete_inactive_resources(cls):
        return cls.objects.filter(is_active=False).delete()

# Модель для экзаменов (пример: mdexam)
class mdexam(models.Model):
    title = models.CharField(max_length=255, verbose_name="Название экзамена")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания записи")
    exam_date = models.DateTimeField(verbose_name="Дата проведения экзамена")
    image = models.ImageField(upload_to='exams/', null=True, blank=True, verbose_name="Задание (картинка)")
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='exams', verbose_name="Пользователи")
    is_public = models.BooleanField(default=False, verbose_name="Опубликовано")

    class Meta:
        verbose_name = "Экзамен"
        verbose_name_plural = "Экзамены"

    def __str__(self):
        return self.title