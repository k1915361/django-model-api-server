# Generated by Django 4.2.11 on 2025-02-04 19:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0016_task_remove_image_dataset_user_delete_csv_dataset_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='DatasetActionSet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
    ]
