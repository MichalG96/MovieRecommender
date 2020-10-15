# Generated by Django 3.1.2 on 2020-10-15 20:27

import datetime
from django.db import migrations, models
import django.db.models.deletion
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('recommender', '0012_auto_20201015_2205'),
    ]

    operations = [
        migrations.AlterField(
            model_name='movieactor',
            name='actor',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='recommender.actor'),
        ),
        migrations.AlterField(
            model_name='rating',
            name='date_rated',
            field=models.DateTimeField(default=datetime.datetime(2020, 10, 15, 20, 27, 39, 816758, tzinfo=utc)),
        ),
    ]
