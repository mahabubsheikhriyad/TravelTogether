# Generated by Django 4.2.13 on 2024-06-13 13:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0009_profile_badges'),
    ]

    operations = [
        migrations.AlterField(
            model_name='badge',
            name='description',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='badge',
            name='name',
            field=models.CharField(max_length=50, unique=True),
        ),
    ]
