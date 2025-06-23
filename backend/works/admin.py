from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from io import BytesIO
from django.utils.html import format_html
from .models import *
from django.urls import path
from django.shortcuts import get_object_or_404
from faker import Faker
import random
from django.contrib.auth import get_user_model
from django.utils import timezone

admin.site.site_header = "Администрирование сайта Андрея Белого"
admin.site.index_title = "Управление контентом"

class RatingInline(GenericTabularInline):
    model = Rating
    extra = 0
    fields = ['user', 'value', 'created_at']
    readonly_fields = ['created_at']

class CommentInline(GenericTabularInline):
    model = Comment
    extra = 0
    fields = ['user', 'text', 'created_at']
    readonly_fields = ['created_at']

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'date_joined', 'is_staff')
    list_filter = ('is_staff', 'is_superuser')
    search_fields = ('username', 'email')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Персональные данные', {'fields': ('email', 'avatar')}),
        ('Права доступа', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups')}),
    )

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'updated_at')
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title', 'content')
    list_filter = ('created_at',)
    inlines = [RatingInline, CommentInline]
    readonly_fields = ('created_at', 'updated_at')
    slug = models.SlugField(blank=True, unique=True)
    

class ProductAuthorInline(admin.TabularInline):
    model = ProductAuthor
    extra = 1
    verbose_name = "Автор"
    verbose_name_plural = "Авторы"

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'category', 'average_rating', 'is_available', 'status', 'pdf_preview', 'generate_pdf_button')
    list_filter = ('category', 'is_available', 'status')
    search_fields = ('title', 'description')
    readonly_fields = ('average_rating', 'created_at', 'updated_at', 'pdf_preview')
    actions = ['generate_pdf']
    inlines = [ProductAuthorInline]
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'description', 'price', 'category')
        }),
        ('Медиафайлы', {
            'fields': ('image', 'pdf_file', 'pdf_preview')
        }),
        ('Статус и наличие', {
            'fields': ('is_available', 'status', 'quantity')
        }),
        ('Рейтинг и даты', {
            'fields': ('average_rating', 'created_at', 'updated_at')
        }),
    )

    def pdf_preview(self, obj):
        if obj.pdf_file:
            return format_html(
                '<a href="{}" target="_blank">Просмотреть PDF</a> | '
                '<a href="{}" download>Скачать PDF</a>',
                obj.pdf_file.url,
                obj.pdf_file.url
            )
        return "PDF не загружен"
    pdf_preview.short_description = 'PDF документ'

    def generate_pdf_button(self, obj):
        return format_html(
            '<a class="button" href="{}">Сгенерировать PDF</a>',
            reverse('admin:generate-product-pdf', args=[obj.pk])
        )
    generate_pdf_button.short_description = 'Генерация PDF'
    generate_pdf_button.allow_tags = True

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:product_id>/generate-pdf/',
                self.admin_site.admin_view(self.generate_pdf_view),
                name='generate-product-pdf',
            ),
        ]
        return custom_urls + urls

    def generate_pdf_view(self, request, product_id):
        product = get_object_or_404(Product, pk=product_id)
        return product.get_pdf_response()

    def generate_pdf(self, request, queryset):
        # Создаем буфер для PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        # Создаем стиль для заголовка
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30
        )

        # Создаем стиль для текста
        text_style = ParagraphStyle(
            'CustomText',
            parent=styles['Normal'],
            fontSize=12,
            spaceAfter=12
        )

        for product in queryset:
            # Добавляем заголовок
            story.append(Paragraph(f"Информация о продукте: {product.title}", title_style))
            
            # Добавляем основную информацию
            story.append(Paragraph(f"Описание: {product.description}", text_style))
            story.append(Paragraph(f"Цена: {product.price} ₽", text_style))
            story.append(Paragraph(f"Категория: {product.category}", text_style))
            story.append(Paragraph(f"Средний рейтинг: {product.average_rating}", text_style))
            story.append(Paragraph(f"Статус: {product.status}", text_style))
            
            # Добавляем информацию об авторах
            if product.authors.exists():
                authors_text = "Авторы: " + ", ".join([author.name for author in product.authors.all()])
                story.append(Paragraph(authors_text, text_style))
            
            # Добавляем отступ между продуктами
            story.append(Spacer(1, 30))

        # Создаем PDF
        doc.build(story)
        buffer.seek(0)

        # Создаем HTTP ответ
        response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="products.pdf"'
        return response

    generate_pdf.short_description = "Сгенерировать PDF для выбранных продуктов"

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ['created_at', 'updated_at', 'product_title', 'product_price', 'product_image']
    fields = ['product', 'product_title', 'product_price', 'product_image', 'quantity', 'created_at', 'updated_at']

    def product_title(self, obj):
        return obj.product.title
    product_title.short_description = 'Название товара'

    def product_price(self, obj):
        return f"{obj.product.price} ₽"
    product_price.short_description = 'Цена'

    def product_image(self, obj):
        if obj.product.image:
            return format_html('<img src="{}" width="100" />', obj.product.image.url)
        return "-"
    product_image.short_description = 'Изображение'
    product_image.allow_tags = True

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_active', 'created_at', 'updated_at', 'total_price')
    list_filter = ('is_active', 'created_at')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('created_at', 'updated_at', 'total_price')
    inlines = [CartItemInline]

    def total_price(self, obj):
        return f"{obj.get_total_price()} ₽"
    total_price.short_description = 'Общая стоимость'

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product_title', 'product_price', 'product_image', 'quantity', 'total_price', 'created_at', 'updated_at')
    list_filter = ('created_at',)
    search_fields = ('cart__user__username', 'product__title')
    readonly_fields = ('created_at', 'updated_at', 'product_title', 'product_price', 'product_image', 'total_price')

    def product_title(self, obj):
        return obj.product.title
    product_title.short_description = 'Название товара'

    def product_price(self, obj):
        return f"{obj.product.price} ₽"
    product_price.short_description = 'Цена'

    def product_image(self, obj):
        if obj.product.image:
            return format_html('<img src="{}" width="100" />', obj.product.image.url)
        return "-"
    product_image.short_description = 'Изображение'
    product_image.allow_tags = True

    def total_price(self, obj):
        return f"{obj.get_total_price()} ₽"
    total_price.short_description = 'Общая стоимость'

@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    list_display = ('title', 'address', 'average_rating')
    search_fields = ('title', 'address')
    inlines = [RatingInline, CommentInline]

    def average_rating(self, obj):
        return obj.ratings.aggregate(Avg('value'))['value__avg']
    average_rating.short_description = 'Средний рейтинг'

@admin.register(LiteraryWork)
class LiteraryWorkAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'comment_count')
    search_fields = ('title', 'content')
    inlines = [RatingInline, CommentInline]
    
    def comment_count(self, obj):
        return obj.comments.count()
    comment_count.short_description = 'Комментарии'

@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('user', 'value', 'content_object', 'created_at')
    list_filter = ('value', 'created_at')
    search_fields = ('user__username',)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'truncated_text', 'content_object', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('text', 'user__username')

    def truncated_text(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    truncated_text.short_description = 'Текст комментария'

@admin.register(mdexam)
class mdexamAdmin(admin.ModelAdmin):
    list_display = ("title", "exam_date", "created_at", "is_public")
    search_fields = ("title", "users__email")
    list_filter = ("is_public", "created_at", "exam_date")
    filter_horizontal = ("users",)
    fieldsets = (
        (None, {
            'fields': ("title", "exam_date", "image", "is_public", "users")
        }),
        ("Системная информация", {
            'fields': ("created_at",),
            'classes': ("collapse",),
        }),
    )
    readonly_fields = ("created_at",)

    actions = ["generate_fake_exams"]

    def generate_fake_exams(self, request, queryset):
        fake = Faker()
        User = get_user_model()
        users = list(User.objects.all())
        if len(users) < 2:
            self.message_user(request, "Для генерации экзаменов нужно минимум 2 пользователя.", level='error')
            return
        for _ in range(5):
            exam = mdexam.objects.create(
                title=fake.sentence(nb_words=3),
                exam_date=fake.future_datetime(end_date="+30d", tzinfo=timezone.get_current_timezone()),
                is_public=random.choice([True, False])
            )
            exam.save()
            exam.users.set(random.sample(users, k=random.randint(1, min(3, len(users)))))
        self.message_user(request, "5 фейковых экзаменов успешно добавлены!")
    generate_fake_exams.short_description = "Сгенерировать 5 фейковых экзаменов (Faker)"
