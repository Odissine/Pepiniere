# Generated by Django 3.2.5 on 2023-04-22 16:52

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0008_alter_inventaire_end_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inventaire',
            name='end_date',
            field=models.DateTimeField(default=datetime.datetime(2024, 4, 16, 16, 52, 28, 915371)),
        ),
    ]
