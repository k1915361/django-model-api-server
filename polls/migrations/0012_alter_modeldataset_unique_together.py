# Generated by Django 5.1.2 on 2024-11-18 12:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0011_modeldataset'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='modeldataset',
            unique_together={('model', 'dataset')},
        ),
    ]
