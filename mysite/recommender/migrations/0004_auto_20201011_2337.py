# Generated by Django 3.1.2 on 2020-10-11 21:37

import datetime
from django.db import migrations, models
import django.db.models.deletion
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('recommender', '0003_auto_20201011_2336'),
    ]

    operations = [
        migrations.CreateModel(
            name='Movie',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('movielens_id', models.IntegerField()),
                ('imdb_id', models.IntegerField()),
                ('tmdb_id', models.IntegerField()),
                ('title', models.TextField()),
                ('year_released', models.IntegerField()),
                ('director', models.CharField(max_length=100)),
            ],
        ),
        migrations.AlterField(
            model_name='rating',
            name='date_rated',
            field=models.DateTimeField(default=datetime.datetime(2020, 10, 11, 21, 37, 38, 669948, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='rating',
            name='movielens_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recommender.movie'),
        ),
    ]
