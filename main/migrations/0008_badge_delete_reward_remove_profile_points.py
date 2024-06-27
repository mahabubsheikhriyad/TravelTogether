# Generated by Django 4.2.13 on 2024-06-13 12:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0007_reward_profile_points'),
    ]

    operations = [
        migrations.CreateModel(
            name='Badge',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('tier', models.CharField(choices=[('Bronze', 'Bronze'), ('Silver', 'Silver'), ('Gold', 'Gold'), ('Platinum', 'Platinum')], max_length=10)),
                ('image', models.ImageField(upload_to='badges/')),
            ],
        ),
        migrations.DeleteModel(
            name='Reward',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='points',
        ),
    ]
