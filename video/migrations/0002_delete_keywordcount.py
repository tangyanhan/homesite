# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-10 08:56
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('video', '0001_initial'),
    ]

    operations = [
        migrations.DeleteModel(
            name='KeywordCount',
        ),
    ]
