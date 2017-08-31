# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-08-25 20:11
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organization', '0005_auto_20170825_2011'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='teacher',
            name='course_nums',
        ),
        migrations.RemoveField(
            model_name='teacher',
            name='students',
        ),
        migrations.AddField(
            model_name='courseorg',
            name='course_nums',
            field=models.IntegerField(default=0, verbose_name='课程数'),
        ),
        migrations.AddField(
            model_name='courseorg',
            name='students',
            field=models.IntegerField(default=0, verbose_name='学习人数'),
        ),
    ]