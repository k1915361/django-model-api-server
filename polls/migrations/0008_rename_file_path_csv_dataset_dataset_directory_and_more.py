# Generated by Django 4.2.11 on 2024-11-01 14:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0007_rename_user_id_csv_dataset_user_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='csv_dataset',
            old_name='file_path',
            new_name='dataset_directory',
        ),
        migrations.RenameField(
            model_name='dataset',
            old_name='file_path',
            new_name='dataset_directory',
        ),
        migrations.RenameField(
            model_name='image_dataset',
            old_name='file_path',
            new_name='dataset_directory',
        ),
    ]
