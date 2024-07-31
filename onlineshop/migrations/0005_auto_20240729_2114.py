# Generated by Django 3.2.16 on 2024-07-29 21:14

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('onlineshop', '0004_auto_20231020_2138'),
    ]

    operations = [
        migrations.CreateModel(
            name='DataMapping',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
                ('field', models.TextField()),
                ('model', models.TextField()),
                ('order', models.TextField(blank=True, default=1, null=True)),
            ],
        ),
    ]
