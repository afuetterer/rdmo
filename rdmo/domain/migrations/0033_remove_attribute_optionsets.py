# -*- coding: utf-8 -*-
# Generated by Django 1.11.14 on 2018-07-05 15:22
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('domain', '0032_remove_unit_and_type'),
        ('questions', '0018_data_migration'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='attribute',
            name='optionsets',
        ),
    ]