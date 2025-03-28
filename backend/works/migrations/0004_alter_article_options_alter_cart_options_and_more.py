# Generated by Django 4.2 on 2025-03-24 11:22

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('bely_works', '0003_alter_article_options_alter_cart_options_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='article',
            options={'verbose_name': 'Статья', 'verbose_name_plural': 'Статьи'},
        ),
        migrations.AlterModelOptions(
            name='cart',
            options={'verbose_name': 'Корзина', 'verbose_name_plural': 'Корзины'},
        ),
        migrations.AlterModelOptions(
            name='literarywork',
            options={'verbose_name': 'Произведение', 'verbose_name_plural': 'Произведения'},
        ),
        migrations.AlterModelOptions(
            name='product',
            options={'ordering': ['-created_at', 'title'], 'verbose_name': 'Товар', 'verbose_name_plural': 'Товары'},
        ),
        migrations.AlterModelOptions(
            name='user',
            options={'verbose_name': 'user', 'verbose_name_plural': 'users'},
        ),
        migrations.AddField(
            model_name='product',
            name='category',
            field=models.CharField(choices=[('BOOK', 'Книга'), ('SOUVENIR', 'Сувенир'), ('ARTWORK', 'Арт-объект')], default='BOOK', max_length=20),
        ),
        migrations.AddField(
            model_name='product',
            name='last_modified',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='product',
            name='status',
            field=models.CharField(choices=[('IN_STOCK', 'В наличии'), ('OUT_OF_STOCK', 'Нет в наличии'), ('COMING_SOON', 'Скоро в продаже')], default='IN_STOCK', max_length=20),
        ),
        migrations.AddField(
            model_name='product',
            name='stock_date',
            field=models.DateTimeField(default=django.utils.timezone.now, help_text='Дата поступления на склад'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='product',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.CreateModel(
            name='Promotion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('type', models.CharField(choices=[('DISCOUNT', 'Скидка'), ('SPECIAL', 'Специальное предложение'), ('BUNDLE', 'Комплект')], max_length=20)),
                ('start_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('end_date', models.DateTimeField()),
                ('products', models.ManyToManyField(related_name='promotions', to='bely_works.product')),
            ],
            options={
                'ordering': ['-start_date'],
            },
        ),
    ]
