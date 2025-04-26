from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from works.models import Article, Product, Author, Place, LiteraryWork, Rating, Comment
from faker import Faker
from django.utils.text import slugify
import random
from django.core.files.base import ContentFile
import requests
from io import BytesIO
import uuid

fake = Faker('ru_RU')
User = get_user_model()

class Command(BaseCommand):
    help = 'Populate database with sample data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating sample data...')
        
        # Создаем пользователей
        users = []
        for _ in range(5):
            user = User.objects.create_user(
                username=fake.user_name(),
                email=fake.email(),
                password='password123'
            )
            users.append(user)
        
        # Создаем авторов
        authors = []
        for _ in range(10):
            author = Author.objects.create(
                name=fake.name(),
                bio=fake.text(max_nb_chars=500)
            )
            authors.append(author)
        
        # Создаем статьи
        for _ in range(10):
            title = fake.sentence()
            article = Article.objects.create(
                title=title,
                slug=f"{slugify(title)}-{str(uuid.uuid4())[:8]}",
                content=fake.text(max_nb_chars=1000)
            )
            
            # Добавляем рейтинги и комментарии
            for _ in range(random.randint(1, 5)):
                Rating.objects.create(
                    user=random.choice(users),
                    value=random.randint(1, 5),
                    content_object=article
                )
                
                Comment.objects.create(
                    user=random.choice(users),
                    text=fake.paragraph(),
                    content_object=article
                )
        
        # Создаем продукты
        for _ in range(10):
            product = Product.objects.create(
                title=fake.word(),
                price=random.uniform(10.0, 1000.0),
                description=fake.text(max_nb_chars=500)
            )
            
            # Связываем с авторами
            for _ in range(random.randint(1, 3)):
                product.authors.add(
                    random.choice(authors),
                    through_defaults={'role': random.choice(['AUTHOR', 'ILLUSTRATOR', 'TRANSLATOR'])}
                )
        
        # Создаем места
        for _ in range(10):
            place = Place.objects.create(
                title=fake.company(),
                address=fake.address(),
                description=fake.text(max_nb_chars=500)
            )
            
            # Добавляем рейтинги и комментарии
            for _ in range(random.randint(1, 5)):
                Rating.objects.create(
                    user=random.choice(users),
                    value=random.randint(1, 5),
                    content_object=place
                )
        
        # Создаем литературные произведения
        for _ in range(10):
            work = LiteraryWork.objects.create(
                title=fake.sentence(),
                content=fake.text(max_nb_chars=2000)
            )
            
            # Добавляем рейтинги и комментарии
            for _ in range(random.randint(1, 5)):
                Rating.objects.create(
                    user=random.choice(users),
                    value=random.randint(1, 5),
                    content_object=work
                )
                
                Comment.objects.create(
                    user=random.choice(users),
                    text=fake.paragraph(),
                    content_object=work
                )
        
        self.stdout.write(self.style.SUCCESS('Successfully populated database')) 