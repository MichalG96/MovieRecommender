# Generated by Django 3.1.2 on 2020-11-02 11:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recommender', '0007_auto_20201102_1215'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='predictedrating',
            name='No multiple predicted ratings',
        ),
        migrations.RemoveField(
            model_name='predictedrating',
            name='user',
        ),
    ]
