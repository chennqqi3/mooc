# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-08-30 20:54
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organization', '0008_teacher_age'),
    ]

    operations = [
        migrations.AddField(
            model_name='courseorg',
            name='tag',
            field=models.CharField(default='国内知名', max_length=20, verbose_name='机构标签'),
        ),
    ]
