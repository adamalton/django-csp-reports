# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-04 10:55
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cspreports', '0002_auto_20141011_1800'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='cspreport',
            options={'ordering': ('-created',)},
        ),
    ]
