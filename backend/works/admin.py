from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from .models import *

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
    

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_editable = ('price',)
    search_fields = ('title', 'description')
    inlines = [RatingInline, CommentInline]
    list_display = ('title', 'price', 'created_at') 
    readonly_fields = ('preview_image',) 
    def preview_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="200" />', obj.image.url)
        return "-"
    preview_image.short_description = 'Превью изображения'
    preview_image.allow_tags = True
    def created_at_field(self, obj):
        """Кастомный метод для отображения даты создания"""
        return obj.created_at.strftime("%d.%m.%Y %H:%M")
    created_at_field.short_description = 'Дата добавления'

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
