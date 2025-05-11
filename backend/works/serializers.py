from rest_framework import serializers
from .models import (
    User, Article, Product, Author, Place, LiteraryWork,
    Comment, Rating, Cart, CartItem, ProductAuthor, UserProfile
)
import os

class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    avatar_url = serializers.SerializerMethodField()
    bio = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 
                 'full_name', 'avatar_url', 'bio', 'date_joined', 'avatar']
        read_only_fields = ['id', 'date_joined']

    def get_full_name(self, obj):
        return obj.get_full_name()

    def get_avatar_url(self, obj):
        if obj.avatar:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.avatar.url)
            return obj.avatar.url
        return None

    def get_bio(self, obj):
        if hasattr(obj, 'profile'):
            return obj.profile.bio
        return None

    def update(self, instance, validated_data):
        # Обрабатываем аватар отдельно
        avatar = validated_data.pop('avatar', None)
        if avatar:
            # Удаляем старый аватар, если он существует
            if instance.avatar:
                try:
                    os.remove(instance.avatar.path)
                except (ValueError, OSError):
                    pass
            instance.avatar = avatar

        # Обновляем остальные поля
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance

class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    can_delete = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = ['id', 'user', 'text', 'created_at', 'can_delete']
        read_only_fields = ['user', 'created_at']

    def get_can_delete(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return request.user.is_superuser
        return False

class RatingSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    
    class Meta:
        model = Rating
        fields = ['id', 'user', 'value', 'created_at']

class ArticleSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True, read_only=True)
    ratings = RatingSerializer(many=True, read_only=True)
    average_rating = serializers.SerializerMethodField()
    
    class Meta:
        model = Article
        fields = ['id', 'title', 'slug', 'image', 'content', 'comments', 'ratings', 'average_rating', 'created_at', 'updated_at']
    
    def get_average_rating(self, obj):
        ratings = obj.ratings.all()
        if not ratings:
            return None
        return sum(r.value for r in ratings) / len(ratings)

class ProductSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True, read_only=True)
    ratings = RatingSerializer(many=True, read_only=True)
    average_rating = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'title', 'price', 'image', 'description', 'comments', 'ratings', 'average_rating', 'created_at']

    def get_average_rating(self, obj):
        ratings = obj.ratings.all()
        if not ratings:
            return None
        return sum(r.value for r in ratings) / len(ratings)

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ['id', 'name', 'bio', 'photo']

class PlaceSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True, read_only=True)
    ratings = RatingSerializer(many=True, read_only=True)
    average_rating = serializers.SerializerMethodField()

    class Meta:
        model = Place
        fields = ['id', 'title', 'address', 'description', 'comments', 'ratings', 'average_rating']

    def get_average_rating(self, obj):
        ratings = obj.ratings.all()
        if not ratings:
            return None
        return sum(r.value for r in ratings) / len(ratings)

class LiteraryWorkSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True, read_only=True)
    ratings = RatingSerializer(many=True, read_only=True)
    average_rating = serializers.SerializerMethodField()

    class Meta:
        model = LiteraryWork
        fields = ['id', 'title', 'content', 'image', 'comments', 'ratings', 'average_rating', 'created_at', 'updated_at']

    def get_average_rating(self, obj):
        ratings = obj.ratings.all()
        if not ratings:
            return None
        return sum(r.value for r in ratings) / len(ratings)

class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = UserProfile
        fields = ['user', 'bio', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def update(self, instance, validated_data):
        instance.bio = validated_data.get('bio', instance.bio)
        instance.save()
        return instance

class CartItemSerializer(serializers.ModelSerializer):
    product_title = serializers.CharField(source='product.title', read_only=True)
    product_price = serializers.DecimalField(source='product.price', max_digits=10, decimal_places=2, read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_title', 'product_price', 'quantity', 'total_price']
        read_only_fields = ['id', 'total_price']

    def get_total_price(self, obj):
        return obj.get_total_price()

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_price', 'created_at', 'updated_at']
        read_only_fields = ['id', 'total_price']

    def get_total_price(self, obj):
        return obj.get_total_price()