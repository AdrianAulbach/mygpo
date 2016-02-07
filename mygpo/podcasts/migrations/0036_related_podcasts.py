# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-02-07 17:10
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('podcasts', '0035_django_uuidfield'),
    ]

    operations = [
        migrations.AlterField(
            model_name='podcast',
            name='related_podcasts',
            field=models.ManyToManyField(related_name='_podcast_related_podcasts_+', to='podcasts.Podcast'),
        ),
    ]