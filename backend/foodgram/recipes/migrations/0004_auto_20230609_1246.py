# Generated by Django 3.2.19 on 2023-06-09 09:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0003_alter_tag_color'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='favorite',
            options={'verbose_name': 'Избранное', 'verbose_name_plural': 'Избранное'},
        ),
        migrations.AlterModelOptions(
            name='shoppingcart',
            options={'verbose_name': 'Корзина', 'verbose_name_plural': 'Корзины'},
        ),
    ]