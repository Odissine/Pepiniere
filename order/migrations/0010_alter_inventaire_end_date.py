# Generated by Django 3.2.16 on 2023-10-18 19:03

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0009_alter_inventaire_end_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inventaire',
            name='end_date',
            field=models.DateTimeField(default=datetime.datetime(2024, 10, 12, 19, 3, 7, 829550)),
        ),
    ]
