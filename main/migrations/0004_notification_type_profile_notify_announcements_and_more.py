# Generated by Django 4.2.13 on 2024-06-10 15:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_offer_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='type',
            field=models.CharField(choices=[('Donation', 'Donation'), ('Offer Update', 'Offer Update'), ('Announcement', 'Announcement')], default='General', max_length=20),
        ),
        migrations.AddField(
            model_name='profile',
            name='notify_announcements',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='notify_donations',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='notify_offers',
            field=models.BooleanField(default=True),
        ),
    ]
