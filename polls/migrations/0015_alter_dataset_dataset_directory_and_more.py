# Generated by Django 4.2.11 on 2025-01-20 17:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0014_dataset_unique_dataset_name_user_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dataset',
            name='dataset_directory',
            field=models.CharField(max_length=2048, unique=True),
        ),
        migrations.AlterField(
            model_name='model',
            name='model_directory',
            field=models.CharField(max_length=2048, unique=True),
        ),
    ]
