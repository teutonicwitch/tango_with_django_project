# Generated by Django 2.2.28 on 2024-02-07 13:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rango', '0008_remove_category_slug'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='slug',
            field=models.SlugField(default=''),
            preserve_default=False,
        ),
    ]
