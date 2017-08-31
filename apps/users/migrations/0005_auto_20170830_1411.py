# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-08-30 14:11
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_auto_20170824_2030'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emailverifyrecord',
            name='send_type',
            field=models.CharField(choices=[('register', '注册'), ('forget', '忘记密码'), ('update_email', '修改邮箱')], max_length=20, verbose_name='验证码类型'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='gender',
            field=models.CharField(choices=[('male', '男'), ('female', '女')], default='', max_length=20),
        ),
    ]
