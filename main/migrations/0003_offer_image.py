# Generated by Django 4.2.13 on 2024-06-10 06:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_profile_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='offer',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='offer_images/'),
        ),
    ]
