# -*- coding: utf-8 -*-
# Generated by Django 1.11.14 on 2018-08-29 15:41
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0015_data_migration'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='timeframe',
            name='end_attribute',
        ),
        migrations.RemoveField(
            model_name='timeframe',
            name='start_attribute',
        ),
        migrations.RemoveField(
            model_name='timeframe',
            name='task',
        ),
        migrations.DeleteModel(
            name='TimeFrame',
        ),
    ]